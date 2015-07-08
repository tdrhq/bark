from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import tempfile
import shutil
import os
import subprocess
import bark

from bark import Bark
from source_control import SourceControl, BadRev

from subprocess import *

from os.path import exists

class TestBark(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)
        subprocess.check_output(["git", "init"])
        self.add_commit(a="foobar")

        self.bark = Bark(source_control=SourceControl())

    def tearDown(self):
        os.chdir(self.olddir)
        shutil.rmtree(self.tmpdir)

    def test_setup(self):
        pass

    def add_commit(self, **files):
        for k, v in files.iteritems():
            f = open(str(k), "w")
            f.write(v)
            f.close()

            subprocess.check_output(["git", "add", k])

        subprocess.check_output(["git", "commit", "-a", "-m", "stuff"])
        return subprocess.check_output(["git", 'rev-parse', 'HEAD'])

    def test_add_commit(self):
        h1 = self.add_commit(a="foo")
        h2 = self.add_commit(a="bar")

        self.assertNotEquals(h1, h2)

    def checkout(self, branch_name, parent="HEAD"):
        check_output(["git", "checkout", "-b", branch_name, parent])

    def checkout_old(self, branch_name, parent="HEAD"):
        check_output(["git", "checkout", branch_name])

    def test_list_managed(self):
        self.checkout("foo-branch")
        self.bark.manage_feature("foo-branch")

        self.assertEquals(["foo-branch"], self.bark.list_features())

    def test_non_existent_feature(self):
        try:
            self.bark.manage_feature("doesnotexist")
            self.fail("expected exception")
        except BadRev:
            pass  # expected

    def _build_tree(self):
        self.add_commit(a="foo")

        self.checkout("parent")
        self.add_commit(b="bar")

        self.checkout("child", "parent")
        self.add_commit(c="car")

        self.checkout("otherchild", "parent")
        self.add_commit(c="car2")
        self.bark.manage_feature("parent")
        self.bark.manage_feature("child")
        self.bark.manage_feature("otherchild")

        self.bark._add_dep("otherchild", "parent")
        self.bark._add_dep("child", "parent")

    def test_rebase(self):
        self._build_tree()

        self.checkout_old("parent")
        self.add_commit(z="blah")
        self.bark.rebase_all("child")

        self.checkout_old("child")
        self.assertTrue(exists("z"))

    def test_linear_dep_finder(self):
        self._build_tree()

        self.assertEquals(["parent"], self.bark.get_deps("child"))

    def test_command_line_manage(self):
        self.checkout("foo")
        bark.main(["./a.out", "manage", "foo"])
        self.assertEquals(["foo"], Bark(source_control=SourceControl()).list_features())

    # def test_command_line_add_dep(self):
    #     self.checkout("foo")
    #     self.checkout("bar", "foo")

    #     Bark(source_control=SourceControl()).manage_feature("foo")
    #     Bark(source_control=SourceControl()).manage_feature("bar")

    #     bark.main(["./a.out", "add_dep", "bar", "foo"])
    #     self.assertEquals(["foo"], Bark(source_control=SourceControl()).get_deps("bar"))

    def test_stores_base_rev(self):
        hash = SourceControl().rev_parse()
        self.bark.create_feature("foobar")
        f = self.bark.feature_db.get_feature_by_name("foobar")
        self.assertEquals(hash, f.base_rev)

    def test_create_feature_with_base(self):
        hash = SourceControl().rev_parse()
        self.add_commit(z="blah")

        self.bark.create_feature("foobar", hash)
        f = self.bark.feature_db.get_feature_by_name("foobar")
        self.assertEquals(hash, f.base_rev)


if __name__ == '__main__':
    unittest.main()

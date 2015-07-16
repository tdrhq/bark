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

        self.source_control = SourceControl(master="master")
        self.bark = Bark(source_control=self.source_control)

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
        return subprocess.check_output(["git", 'rev-parse', 'HEAD']).strip()

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
        self.source_control.checkout("master")
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
        self.assertEquals(["foo"], Bark(source_control=self.source_control).list_features())

    def test_command_line_add_dep(self):
        self.checkout("foo")
        self.checkout("bar")

        Bark(source_control=self.source_control).manage_feature("foo")
        Bark(source_control=self.source_control).manage_feature("bar")
        old_bark = bark.instance
        try:
            bark.instance = self.bark
            bark.main(["./a.out", "add_dep", "bar", "foo"])
        finally:
            bark.instance = old_bark
        self.assertEquals(["foo"], Bark(source_control=self.source_control).get_deps("bar"))

    def test_stores_base_rev(self):
        hash = self.source_control.rev_parse()
        self.bark.create_feature("foobar")
        f = self.bark.feature_db.get_feature_by_name("foobar")
        self.assertEquals(hash, f.base_rev)

    def test_create_feature_with_base(self):
        hash = self.source_control.rev_parse()
        self.add_commit(z="blah")

        self.bark.create_feature("foobar", hash)
        f = self.bark.feature_db.get_feature_by_name("foobar")
        self.assertEquals(hash, f.base_rev)

    def test_doesnt_allow_me_to_add_dep_when_base_commit_is_differentt(self):
        self.bark.create_feature("foo")
        self.add_commit(y="bsdfdsf")

        self.source_control.checkout("master")
        self.add_commit(z="boo")

        self.bark.create_feature("bar")
        self.add_commit(zz="dfsdfds")

        self.source_control.checkout("master")
        self.bark.create_feature("booboo")
        self.add_commit(dfd="dfsfs")

        try:
            self.bark.add_dep("booboo", "bar")
            self.fail("expected exception")
        except SystemExit:
            pass  # expected

    def test_rebase_all_rebases_single_branch_onto_master(self):
        self.bark.create_feature("foo")
        self.add_commit(d="foobar")
        self.source_control.checkout("master")
        new_master = self.add_commit(b="blahblah")

        self.source_control.checkout("foo")
        self.bark.rebase_all("foo")

        self.source_control.checkout("foo")
        self.assertTrue(exists("b"))

        self.assertEquals(new_master, self.bark.feature_db.get_feature_by_name("foo").base_rev)

    def test_create_feature_with_feature_should_create_over_master(self):
        master = self.add_commit(c="fdfd")
        self.bark.create_feature("foo")
        self.add_commit(d="dfdfds")
        self.bark.create_feature("bar")

        self.assertEquals(master, self.source_control.rev_parse())

    def test_delete_feature(self):
        self.bark.create_feature("foo")
        self.source_control.checkout("master")
        self.bark.delete_feature("foo")
        self.assertEquals([], self.bark.list_features())

    def test_delete_feature_when_more_features_exist(self):
        self.bark.create_feature("bar")
        self.bark.create_feature("foo")
        self.source_control.checkout("master")
        self.bark.delete_feature("foo")
        self.assertEquals(["bar"], self.bark.list_features())

    def test_delete_feature_when_more_features_different_order(self):
        self.bark.create_feature("foo")
        self.bark.create_feature("bar")
        self.source_control.checkout("master")
        self.bark.delete_feature("foo")
        self.assertEquals(["bar"], self.bark.list_features())

    def test_delete_current_feature(self):
        master = self.add_commit(b="cdf")
        self.bark.create_feature("foo")
        foo = self.add_commit(c="dfsdf")

        self.bark.delete_feature("foo")
        self.assertEquals([], self.bark.list_features())
        self.assertEquals(master, self.source_control.rev_parse())

    def test_complete_linear_feature(self):
        master = self.add_commit(bb="boo")
        self.bark.create_feature("foo")
        self.add_commit(dd="blah")
        self.bark.create_feature("bar")
        self.add_commit(ee="sdfdsf")
        self.source_control.checkout("master")
        self.bark.complete_feature("foo")

        self.assertEquals([], self.bark.feature_db.get_feature_by_name("bar").deps)

        self.source_control.checkout("bar")
        self.assertTrue(os.path.exists("ee"))
        self.assertFalse(os.path.exists("dd"))
        try:
            self.source_control.rev_parse("foo")
            self.fail("expected foo to not exist")
        except BadRev:
            pass  # expected

    def test_complete_current_feature(self):
        master = self.add_commit(bb="boo")
        self.bark.create_feature("foo")
        self.add_commit(cc="ddd")

        self.bark.complete_feature("foo")
        self.assertFalse(os.path.exists("cc"))
        try:
            self.source_control.rev_parse("foo")
            self.fail("expected foo to not exist")
        except BadRev:
            pass  # expected

if __name__ == '__main__':
    unittest.main()

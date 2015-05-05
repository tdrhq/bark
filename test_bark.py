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
from subprocess import *

class TestBark(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)
        subprocess.check_output(["git", "init"])
        self.add_commit(a="foobar")

        self.bark = Bark()

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

    def test_list_managed(self):
        self.checkout("foo-branch")
        self.bark.manage_feature("foo-branch")

        self.assertEquals(["foo-branch"], self.bark.list_features())

    def test_non_existent_feature(self):
        try:
            self.bark.manage_feature("doesnotexist")
            self.fail("expected exception")
        except bark.BadArgs:
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



    def test_linear_dep_finder(self):
        self._build_tree()

        self.assertEquals(["parent"], self.bark.get_deps("child"))

    def test_direct_deps(self):
        self._build_tree()

        self.checkout("child3", "child")
        self.bark.manage_feature("child3")

        subprocess.check_call("git log --graph -a | cat", shell=True)

        self.assertEquals(["parent", "child"], self.bark.get_deps("child3"))

if __name__ == '__main__':
    unittest.main()

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import tempfile
import shutil
import os
import subprocess

from bark import Bark
from subprocess import *

class TestBark(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)
        subprocess.check_output(["git", "init"])
        self.add_commit("foobar")

        self.bark = Bark()

    def tearDown(self):
        os.chdir(self.olddir)
        shutil.rmtree(self.tmpdir)

    def test_setup(self):
        pass

    def add_commit(self, text):
        f = open("myfile.txt", "w")
        f.write(text)
        f.close()

        subprocess.check_output(["git", "add", "myfile.txt"])
        subprocess.check_output(["git", "commit", "-a", "-m", "stuff"])

        return subprocess.check_output(["git", 'rev-parse', 'HEAD'])

    def test_add_commit(self):
        h1 = self.add_commit("foo")
        h2 = self.add_commit("bar")

        self.assertNotEquals(h1, h2)

    def checkout(self, branch_name):
        check_output(["git", "checkout", "-b", branch_name])

    def test_list_managed(self):
        self.checkout("foo-branch")
        self.bark.manage_feature("foo-branch")

        self.assertEquals(["foo-branch"], self.bark.list_features())

if __name__ == '__main__':
    unittest.main()

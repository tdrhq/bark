from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import tempfile
import shutil
import os
import subprocess

class TestBark(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)
        subprocess.check_output(["git", "init"])
        self.add_commit("foobar")

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

if __name__ == '__main__':
    unittest.main()

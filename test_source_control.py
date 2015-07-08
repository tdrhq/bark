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

from source_control import SourceControl
from subprocess import *

from os.path import exists

class TestSourceControl(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.olddir = os.getcwd()
        os.chdir(self.tmpdir)
        subprocess.check_output(["git", "init"])
        self.add_commit(a="foobar")

        self.sc = SourceControl()

    def add_commit(self, **files):
        for k, v in files.iteritems():
            f = open(str(k), "w")
            f.write(v)
            f.close()

            subprocess.check_output(["git", "add", k])

        subprocess.check_output(["git", "commit", "-a", "-m", "stuff"])
        return subprocess.check_output(["git", 'rev-parse', 'HEAD'])

    def tearDown(self):
        os.chdir(self.olddir)
        shutil.rmtree(self.tmpdir)

    def test_add_branch(self):
        self.sc.add_branch("foobar")
        self.assertEquals("foobar", self.sc.current_branch())

    def test_delete_branch(self):
        self.sc.add_branch("foobar")
        self.sc.add_branch("foobar3")
        self.sc.delete_branch("foobar")

        self.assertNotEquals(
            0,
            subprocess.call(["git", 'rev-parse', "foobar"]))
        self.assertEquals(
            0,
            subprocess.call(["git", 'rev-parse', "foobar3"]))


    def test_get_hash(self):
        self.sc.add_branch("blah")
        hash1 = self.sc.rev_parse("blah")
        self.add_commit(b="boo")
        hash2 = self.sc.rev_parse("blah")

        self.assertEquals(40, len(hash1))
        self.assertNotEquals(hash1, hash2)


if __name__ == '__main__':
    unittest.main()
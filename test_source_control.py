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

    def test_checkout(self):
        self.sc.add_branch("blah")
        self.sc.add_branch("blah2")
        self.sc.checkout("blah")
        self.assertEquals("blah", self.sc.current_branch())

    def test_master_merge_point(self):
        self.sc.add_branch("blah")
        self.add_commit(b="boo")
        merge_point = self.sc.rev_parse()

        self.sc.add_branch("blah2")
        self.add_commit(d="dfsfdsf")
        self.sc.checkout("blah")
        self.add_commit(c="gah")

        sc = SourceControl(master="blah")
        self.assertEquals(merge_point, sc.get_master_merge_point("blah2"))

    def test_is_clean(self):
        self.assertTrue(self.sc.is_clean())
        with open("a", "w") as f:
            f.write("blah2")

        self.assertFalse(self.sc.is_clean())

    def test_merge(self):
        self.sc.add_branch("blah")
        self.add_commit(b="woo")
        self.sc.checkout("master")
        self.sc.add_branch("blah2")
        self.add_commit(d="blahhh")

        self.sc.merge("blah")
        self.assertTrue(exists("b"))
        self.assertTrue(exists("d"))
        self.assertTrue(self.sc.is_clean())

    def test_multi_merge_with_two(self):
        self.test_merge()
        self.sc.checkout("master")
        self.sc.add_branch("blah3")
        self.add_commit(f="sdfdsfdsf")

        self.sc.checkout("master")

        rev = self.sc.multi_merge(["blah", "blah2", "blah3"])
        self.assertNotEquals(None, rev)

        self.sc.checkout(rev)

        self.assertTrue(exists("b"))
        self.assertTrue(exists("d"))
        self.assertTrue(exists("f"))

if __name__ == '__main__':
    unittest.main()

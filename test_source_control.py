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


if __name__ == '__main__':
    unittest.main()

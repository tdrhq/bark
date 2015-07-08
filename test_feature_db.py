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

from feature_db import FeatureDb, Feature

from subprocess import *

from os.path import exists

class TestFeatureDb(unittest.TestCase):
    def setUp(self):
        self.filename = tempfile.mktemp()
        self.feature_db = FeatureDb(filename=self.filename)

    def tearDown(self):
        if exists(self.filename):
            os.remove(self.filename)

    def test_stuff(self):
        pass


    def test_stores_stuff(self):
        f = Feature()
        f.name = "boo"
        f.deps = ["ab", "c"]
        f.base_rev = "blah"

        self.feature_db.add_feature(f)

        ff = self.feature_db.get_feature_by_name("boo")

        self.assertEquals("boo", ff.name)
        self.assertEquals(["ab", "c"], ff.deps)
        self.assertEquals("blah", ff.base_rev)

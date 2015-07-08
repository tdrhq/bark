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
from feature_db import FeatureDb

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

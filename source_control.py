#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import subprocess
import os
import sys

class SourceControl:
    def add_branch(self, name):
        subprocess.check_call(["git", "checkout", "-b", name])

    def delete_branch(self, name):
        subprocess.check_call(["git", "branch", "-d", name])

    def current_branch(self):
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def rev_parse(self, rev="HEAD"):
        return subprocess.check_output(["git", "rev-parse", rev]).strip()

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

class BadRev(BaseException):
    pass

class SourceControl:
    def __init__(self, master="origin/master"):
        self.master = master

    def add_branch(self, name):
        subprocess.check_call(["git", "checkout", "-b", name])

    def checkout(self, name):
        subprocess.check_call(["git", "checkout", name])

    def delete_branch(self, name):
        subprocess.check_call(["git", "branch", "-d", name])

    def rebase(self, onto):
        subprocess.check_call(["git", "rebase", onto])

    def current_branch(self):
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def rev_parse(self, rev="HEAD"):
        try:
            return subprocess.check_output(["git", "rev-parse", rev]).strip()
        except subprocess.CalledProcessError:
            raise BadRev()

    def get_master_merge_point(self, rev):
        return subprocess.check_output(["git", "merge-base", rev, self.master]).strip()

    def is_clean(self):
        return subprocess.call(["git", "diff-index", "--quiet", "HEAD"]) == 0


    def merge(self, other_rev):
        subprocess.check_call(["git", "merge", "--quiet", "-m", "merge point", other_rev])

    def multi_merge(self, revs):
        assert self.is_clean()
        self.checkout(self.rev_parse())

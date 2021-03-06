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

class NotARepo(BaseException):
    pass

class SourceControl:
    def __init__(self, master="origin/master"):
        self._master = master

    def add_branch(self, name, parent=None):
        cmd = ["git", "checkout", "-b", name]
        if parent:
            cmd.append(parent)
        subprocess.check_call(cmd)

    def master(self):
        return self._master

    def get_root(self):
        curdir = os.getcwd()

        while not os.path.exists(os.path.join(curdir, ".git")):
            curdir = os.path.abspath(curdir + "/..")

            if curdir == "/":
                raise NotARepo()

        return curdir

    def checkout(self, name):
        subprocess.check_call(["git", "checkout", name])

    def delete_branch(self, name):
        print("Deleting branch %s which was at rev: %s" % (name, self.rev_parse(name)))
        subprocess.check_call(["git", "branch", "-D", name])

    def rebase(self, onto, base=None):
        if not base:
            subprocess.check_call(["git", "rebase", onto])
        else:
            subprocess.check_call(["git", "rebase", "--onto", onto, base])

    def current_branch(self):
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def rev_parse(self, rev="HEAD"):
        try:
            return subprocess.check_output(["git", "rev-parse", rev]).strip()
        except subprocess.CalledProcessError:
            raise BadRev()

    def get_master_merge_point(self, rev):
        return subprocess.check_output(["git", "merge-base", rev, self._master]).strip()

    def is_clean(self):
        return subprocess.call(["git", "diff-index", "--quiet", "HEAD"]) == 0


    def merge(self, other_rev):
        subprocess.check_call(["git", "merge", "--quiet", "-m", "merge point", other_rev])

    def multi_merge(self, revs):
        assert self.is_clean()
        return self._rec_merge(revs)

    def _rec_merge(self, revs):
        if len(revs) == 1:
            return self.rev_parse(revs[0])

        if len(revs) == 2:
            self.checkout(self.rev_parse(revs[0]))
            self.merge(revs[1])
            return self.rev_parse()

        return self._rec_merge([self._rec_merge(revs[0:-1]), revs[-1]])

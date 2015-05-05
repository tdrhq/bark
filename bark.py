#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import subprocess
import os

FEATURE_FILE = '.bark_features'

class BadArgs(BaseException):
    pass

def _rev_parse(rev):
    return subprocess.check_output(['git', 'rev-parse', rev]).strip()

class Bark:
    def manage_feature(self, feature):
        if subprocess.call(['git', 'rev-parse', feature]) != 0:
            raise BadArgs()

        with open(FEATURE_FILE, "a") as f:
            f.write(feature + "\n")

    def list_features(self):
        with open(FEATURE_FILE, "r") as f:
            return f.read().strip().splitlines()

    def get_deps(self, feature):
        ret = []
        for other in self.list_features():
            if other == feature:
                continue

            merge_base = subprocess.check_output(['git', 'merge-base', other, feature]).strip()
            other_rev = _rev_parse(other)

            if other_rev == merge_base:
                ret.append(other)

        return ret

    def get_direct_deps(self, feature):
        all_deps = self.get_deps(feature)
        copy = list(all_deps)
        for d in copy:
            sub_deps = self.get_deps(d)
            for sub_dep in sub_deps:
                if sub_dep in all_deps:
                    all_deps.remove(sub_dep)

        return all_deps

def usage():
    print("unimplemented")
    sys.exit(1)

def cmd_feature(args, options):
    feature_name = args[1]

def main(argv):
    logging
    try:
        options, rest_args = getopt.gnu_getopt(
            argv[1:],
            "",
            [
            ]
        )
    except getopt.GetoptError as e:
        print(e.msg + "\n")
        usage()
        return 1

    command = rest_args[0]

    if command.equals(feature):
        cmd_feature(rest_args, options)

if __name__ == '__main__':
    main(sys.argv)

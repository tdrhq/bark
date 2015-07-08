#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import os
import sys
from source_control import BadRev

from source_control import SourceControl

FEATURE_FILE = '.bark_features'

class BadArgs(BaseException):
    pass

class Bark:
    def __init__(self, source_control):
        self.source_control = source_control

    def manage_feature(self, feature):
        self.source_control.rev_parse(feature)

        with open(FEATURE_FILE, "a") as f:
            f.write(feature + "\n")

    def delete_feature(self, feature):
        # verify feature is not referenced from another feature
        features = self._read_features()
        for name, deps in features.iteritems():
            for f in deps:
                if f == feature:
                    raise RuntimeError("Dep in use")

        del features[feature]
        self._write_features(features)

    def list_features(self):
        return list(self._read_features().iterkeys())

    def _read_features(self):
        ret = {}
        with open(FEATURE_FILE, "r") as f:
            lines = f.read().strip().splitlines()

            for line in lines:
                words = line.split()
                ret[words[0]] = words[1:]

        return ret

    def _write_features(self, features):
        with open(FEATURE_FILE, "w") as f:
            for feature, deps in features.iteritems():
                f.write(feature)

                for d in deps:
                    f.write(" ")
                    f.write(d)

                f.write("\n")

    def add_dep(self, child, parent):
        deps = self._read_features()

        deps[child] += [parent]

        self._write_features(deps)

    def get_deps(self, feature):
        return self._read_features()[feature]

    def rebase_all(self, feature):
        deps = self.get_deps(feature)

        # make sure all children are up-to-date before doing anything
        for d in deps:
            print("first updating " + d)
            self.rebase_all(d)

        if len(deps) == 0:
            return

        self.source_control.checkout(feature)

        if len(deps) == 1:
            self.source_control.rebase(deps[0])
            return

        raise RuntimeError("unsupported, too many deps" + str(deps))

def usage():
    print("unimplemented")
    sys.exit(1)

def cmd_feature(args, options):
    feature_name = args[1]
    source_control.add_branch(feature_name)
    instance.manage_feature(feature_name)

def delete_feature(args):
    feature_name = args[1]
    instance.delete_feature(feature_name)
    source_control.delete_branch(feature_name)

source_control = SourceControl()
instance = Bark(source_control=source_control)

def manage(rest_args, root_options):
    branch = rest_args
    instance.manage_feature(rest_args[1])

def main(argv):
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

    if command == "manage":
        manage(rest_args, options)
    elif command == "rebaseall":
        instance.rebase_all(rest_args[1])
    elif command == "add_dep":
        instance.add_dep(rest_args[1], rest_args[2])
    elif command =="feature":
        cmd_feature(rest_args, options)
    elif command == "delete-feature":
        delete_feature(rest_args)
    else:
        raise RuntimeError("unsupported")

    return 0

if __name__ == '__main__':
    main(sys.argv)

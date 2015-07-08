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
from feature_db import FeatureDb, Feature

class BadArgs(BaseException):
    pass

class Bark:
    def __init__(self, source_control):
        self.source_control = source_control
        self.feature_db = FeatureDb()

    def manage_feature(self, feature):
        self.source_control.rev_parse(feature)

        f = Feature()
        f.name = feature
        self.feature_db.add_feature(f)

    def delete_feature(self, feature):
        # verify feature is not referenced from another feature
        features = self._read_features()
        for name, deps in features.iteritems():
            for f in deps:
                if f == feature:
                    raise RuntimeError("Dep in use")

        self.delete_feature_by_name(feature)

    def list_features(self):
        return [f.name for f in self.feature_db._read_features()]

    def _get_feature_for(self, name):
        features = self.feature_db._read_features()
        for f in features:
            if f.name == name:
                return f

    def add_dep(self, child, parent):
        features = self.feature_db._read_features()

        for f in features:
            if f.name == child:
                f.deps += [parent]

        self.feature_db._write_features(features)

    def get_deps(self, feature):
        return self._get_feature_for(feature).deps

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

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

    def manage_feature(self, feature, base_rev=None):
        self.source_control.rev_parse(feature)

        f = Feature()
        f.name = feature
        f.base_rev = base_rev
        self.feature_db.add_feature(f)

    def create_feature(self, name, parent=None):
        self.source_control.add_branch(name, parent)
        self.manage_feature(name, base_rev=source_control.rev_parse())

    def add_dep(self, name, parent):
        self._add_dep(name, parent)
        feature = self.feature_db.get_feature_by_name(name)
        merge_point = self.source_control.multi_merge(feature.deps)

        self.source_control.checkout(feature.name)
        self.source_control.rebase(merge_point, feature.base_rev)

        feature.base_rev = merge_point
        self.feature_db.update_feature(feature)

    def delete_feature(self, feature):
        # verify feature is not referenced from another feature
        features = self.feature_db.list_features()
        for name, deps in features.iteritems():
            for f in deps:
                if f == feature:
                    raise RuntimeError("Dep in use")

        self.delete_feature_by_name(feature)

    def list_features(self):
        return [f.name for f in self.feature_db.list_features()]

    def _get_feature_for(self, name):
        features = self.feature_db.list_features()
        for f in features:
            if f.name == name:
                return f

    def _add_dep(self, child, parent):
        f = self.feature_db.get_feature_by_name(child)
        f.deps += [parent]

        self.feature_db.update_feature(f)

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
    bark.create_feature(feature_name)

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

#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
sys.path.append(os.path.dirname(__file__) + "/toposort-1.4")

import toposort

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
        if not parent:
            parent = self.source_control.master()
        self.source_control.add_branch(name, parent)
        self.manage_feature(name, base_rev=source_control.rev_parse())

    def _validate_mergeable(self):
        features = self.list_features()
        merge_bases = [self.source_control.get_master_merge_point(f) for f in features]
        print("stuff %s"  % merge_bases)
        if len(set(merge_bases)) > 1:
            print('All branches need to have the same merge point with maser, run "bark rebaseall"')
            exit(1)

    def add_dep(self, name, parent):
        self._validate_mergeable()
        self._add_dep(name, parent)
        feature = self.feature_db.get_feature_by_name(name)
        merge_point = self.source_control.multi_merge(feature.deps)

        self.source_control.checkout(feature.name)
        self.source_control.rebase(merge_point, feature.base_rev)

        feature.base_rev = merge_point
        self.feature_db.update_feature(feature)

    def delete_feature(self, feature_name):
        # verify feature is not referenced from another feature
        features = self.feature_db.list_features()
        for feature in features:
            for f in feature.deps:
                if f == feature.name:
                    raise RuntimeError("Dep in use")

        # move to master if we're on the deleted branch
        if self.source_control.current_branch() == feature_name:
            self.source_control.checkout(self.source_control.master())

        self.feature_db.delete_feature_by_name(feature_name)
        source_control.delete_branch(feature_name)

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
        f = self.feature_db.get_feature_by_name(feature)
        deps = self.get_deps(feature)

        # make sure all children are up-to-date before doing anything
        for d in deps:
            print("first updating " + d)
            self.rebase_all(d)

        merge_point = self.source_control.rev_parse(self.source_control.master())

        if len(deps) > 0:
            merge_point = self.source_control.multi_merge(deps)


        self.source_control.checkout(feature)
        self.source_control.rebase(merge_point, base=f.base_rev)
        f.base_rev = merge_point
        self.feature_db.update_feature(f)

def usage():
    print("unimplemented")
    sys.exit(1)

def cmd_feature(args, options):
    feature_name = args[1]
    dep = (args[2] if len(args) == 3 else None)
    instance.create_feature(feature_name, parent=dep)

def delete_feature(args):
    feature_name = args[1]
    instance.delete_feature(feature_name)

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
    elif command == "complete":
        instance.complete_feature(argv[1])
    else:
        raise RuntimeError("unsupported")

    return 0

if __name__ == '__main__':
    main(sys.argv)

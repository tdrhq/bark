#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import os
import sys


FEATURE_FILE = '.bark_features'


class Feature:
    def __init__(self):
        self.name = None
        self.deps = []
        self.base_rev = None

class FeatureDb:
    def __init__(self, filename=FEATURE_FILE):
        self.filename = filename

    def _read_features(self):
        ret = []

        if not os.path.exists(self.filename):
            return []

        with open(self.filename, "r") as f:
            lines = f.read().strip().splitlines()

            for line in lines:
                words = line.split()
                f = Feature()
                f.name = words[0]
                f.deps = words[1:]
                ret.append(f)

        return ret

    def list_features(self):
        return self._read_features()

    def _write_features(self, features):
        with open(self.filename, "w") as f:
            for feature in features:
                f.write(feature.name)

                for d in feature.deps:
                    f.write(" ")
                    f.write(d)

                f.write("\n")


    def add_feature(self, feature):
        features = self._read_features()
        features.append(feature)
        self._write_features(features)

    def delete_feature_by_name(self, feature_name):
        features = self._read_features()
        features = [x for x in features if x.name != feature_name]
        self._write_features(features)

    def get_feature_by_name(self, feature_name):
        for x in self._read_features():
            if x.name == feature_name:
                return x

    def update_feature(self, feature):
        self.delete_feature_by_name(feature.name)
        self.add_feature(feature)
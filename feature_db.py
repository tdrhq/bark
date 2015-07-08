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
    def _read_features(self):
        ret = []

        if not os.path.exists(FEATURE_FILE):
            return []

        with open(FEATURE_FILE, "r") as f:
            lines = f.read().strip().splitlines()

            for line in lines:
                words = line.split()
                f = Feature()
                f.name = words[0]
                f.deps = words[1:]
                ret.append(f)

        return ret

    def _write_features(self, features):
        with open(FEATURE_FILE, "w") as f:
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

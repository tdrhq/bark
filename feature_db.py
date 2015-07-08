#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import os
import sys
import json

FEATURE_FILE = '.bark_features'


class Feature:
    def __init__(self):
        self.name = None
        self.deps = []
        self.base_rev = None

class FeatureDb:
    def __init__(self, filename=FEATURE_FILE):
        self.filename = filename


    def _to_json_array(self, features):
        ret = []
        for f in features:
            ret.append({
                "name": f.name,
                "deps": f.deps,
                "base_rev": f.base_rev,
            })
        return ret

    def _from_json_array(self, array):
        ret = []
        for f in array:
            ff = Feature()
            ff.name = f["name"]
            ff.deps = f["deps"]
            ff.base_rev = f["base_rev"]
            ret.append(ff)

        return ret

    def _read_features(self):
        ret = []

        if not os.path.exists(self.filename):
            return []

        with open(self.filename, "r") as f:
            s = f.read()
            print("json is " + s)
            return self._from_json_array(json.loads(s))

    def list_features(self):
        return self._read_features()

    def _write_features(self, features):
        with open(self.filename, "w") as f:
            json.dump(self._to_json_array(features), f)

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

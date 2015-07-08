#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import logging
import os
import sys

class Feature:
    def __init__(self):
        self.name = None
        self.deps = []
        self.base_rev = None

class FeatureDb:
    pass

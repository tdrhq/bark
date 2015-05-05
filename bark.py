#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt

import loggin

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

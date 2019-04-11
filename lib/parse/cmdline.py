#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-04-11 20:07:47
'''

import sys
import argparse

def cmdLineParser():
    """
    This function parses the command line parameters and arguments
    """
    parser = argparse.ArgumentParser(usage="python3 dirmap.py -iU https://target.com -lcf")

    # engine
    engine = parser.add_argument_group("Engine", "Engine config")
    engine.add_argument("-t","--thread",  dest="thread_num", type=int, default=30,
                        help="num of threads, default 30")

    # target
    target = parser.add_argument_group("Target","Target config")
    target.add_argument("-iU", metavar="TARGET", dest="target_single", type=str, default="",
                        help="scan a single target (e.g. http://target.com)")
    target.add_argument("-iF", metavar="FILE", dest="target_file", type=str, default="",
                        help="load targets from targetFile (e.g. urls.txt)")
    target.add_argument("-iR", metavar="START-END", dest="target_range", type=str, default="",
                        help="array from int(start) to int(end) (e.g. 192.168.1.1-192.168.2.100)")
    target.add_argument("-iN", metavar="IP/MASK", dest="target_network", type=str, default="",
                        help="generate IP from IP/MASK. (e.g. 192.168.1.0/24)")

    # bruter
    bruter = parser.add_argument_group("Bruter", "Bruter config")
    bruter.add_argument("-lcf", "--loadConfigFile",  dest="load_config_file", default=False, action="store_true",
                        help="Load the configuration through the configuration file")
    bruter.add_argument("--debug", dest="debug",default=False, action="store_true",
                        help="Print payloads and exit")

    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = parser.parse_args()
    return args

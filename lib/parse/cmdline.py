#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import argparse

def cmdLineParser():
    """
    This function parses the command line parameters and arguments
    """
    parser = argparse.ArgumentParser(usage="python3 dirmap.py -i https://target.com -lcf")

    # engine
    engine = parser.add_argument_group("Engine", "Engine config")
    engine.add_argument("-t","--thread",  dest="thread_num", type=int, default=30,
                        help="num of threads, default 30")

    # target
    target = parser.add_argument_group("Target","Target config")
    target.add_argument("-i", metavar="TARGET", dest="target_input", type=str, default="",
                        help="scan a target or network (e.g. [http://]target.com , 192.168.1.1[/24] , 192.168.1.1-192.168.1.100)")
    target.add_argument("-iF", metavar="FILE", dest="target_file", type=str, default="",
                        help="load targets from targetFile (e.g. urls.txt)")

    # bruter
    bruter = parser.add_argument_group("Bruter", "Bruter config")
    bruter.add_argument("-lcf", "--loadConfigFile",  dest="load_config_file", default=True, action="store_true",
                        help="Load the configuration through the configuration file")
    bruter.add_argument("--debug", dest="debug",default=False, action="store_true",
                        help="Print payloads and exit")

    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = parser.parse_args()
    return args

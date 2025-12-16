#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from gevent import monkey
monkey.patch_all()
from lib.controller.engine import run
from lib.core.common import outputscreen, setPaths
from lib.core.data import cmdLineOptions, conf, paths
from lib.core.option import initOptions
from lib.parse.cmdline import cmdLineParser




def main():
    """
    main fuction of dirmap 
    """
    # Make sure the version of python you are using is high enough
    if sys.version_info < (3, 8):
        outputscreen.error("Sorry, dirmap requires Python 3.8 or higher\n")
        sys.exit(1)
   

    # set paths of project 
    paths.ROOT_PATH = os.getcwd() 
    setPaths()
    
    # received command >> cmdLineOptions
    cmdLineOptions.update(cmdLineParser().__dict__)
    
    # loader script,target,working way(threads? gevent?),output_file from cmdLineOptions
    # and send it to conf
    initOptions(cmdLineOptions) 

    # run!
    try:
        run()
    except KeyboardInterrupt:
        outputscreen.success("[+] exit")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:59
@LastEditTime: 2019-05-01 17:57:11
'''

import os
import sys

from gevent import monkey
monkey.patch_all()
from lib.controller.engine import run
from lib.core.common import banner, outputscreen, setPaths
from lib.core.data import cmdLineOptions, conf, paths
from lib.core.option import initOptions
from lib.parse.cmdline import cmdLineParser




def main():
    """
    main fuction of dirmap 
    """

    # anyway output thr banner information
    banner() 

    # set paths of project 
    paths.ROOT_PATH = os.getcwd() 
    setPaths()
    
    # received command >> cmdLineOptions
    cmdLineOptions.update(cmdLineParser().__dict__)
    
    # loader script,target,working way(threads? gevent?),output_file from cmdLineOptions
    # and send it to conf
    initOptions(cmdLineOptions) 

    # run!
    run()

if __name__ == "__main__":
    main()

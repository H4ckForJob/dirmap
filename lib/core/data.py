#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-04-10 17:46:40
'''

from lib.core.datatype import AttribDict

# dirmap paths
paths = AttribDict()

# object to store original command line options
cmdLineOptions = AttribDict()

# object to share within function and classes command
# line options and settings
conf = AttribDict()

# object to control engine 
th = AttribDict()

#创建payloads字典对象存储payloads
payloads = AttribDict()

#创建tasks字典对象存储tasks
tasks = AttribDict()

#创建进度条对象存储进度
bar = AttribDict()
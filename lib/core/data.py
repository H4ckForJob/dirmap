#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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

# Create payloads dictionary object to store payloads
payloads = AttribDict()

# Create tasks dictionary object to store tasks
tasks = AttribDict()

# Create progress bar object to store progress
bar = AttribDict()
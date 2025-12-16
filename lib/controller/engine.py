#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
import sys
import time
import traceback
from lib.core.data import conf,paths,th
from lib.core.common import outputscreen
from lib.core.enums import BRUTER_RESULT_STATUS
from lib.utils.console import getTerminalSize
from lib.controller.bruter import bruter

def initEngine():
    # init control parameter
    th.result = []
    th.thread_num = conf.thread_num
    th.target = conf.target
    # Whether to continue scanning flag
    th.is_continue = True
    # Console width
    th.console_width = getTerminalSize()[0] - 2
    # Record start time
    th.start_time = time.time()
    msg = '[+] Set the number of thread: %d' % th.thread_num
    outputscreen.success(msg)

def scan():
    while True:
        # Coroutine mode
        if th.target.qsize() > 0 and th.is_continue:
            target = str(th.target.get(timeout=1.0))
        else:
            break
        try:
            # Perform detection on each target
            bruter(target)
        except Exception:
            # When exception is thrown, add errmsg key-value
            th.errmsg = traceback.format_exc()
            th.is_continue = False

def run():
    initEngine()
    # Coroutine mode
    outputscreen.success('[+] Coroutine mode')
    gevent.joinall([gevent.spawn(scan) for i in range(0, th.thread_num)])
    if 'errmsg' in th:
        outputscreen.error(th.errmsg)

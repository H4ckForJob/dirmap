#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-04-11 14:20:32
'''

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
    #是否继续扫描标志位
    th.is_continue = True
    #控制台宽度
    th.console_width = getTerminalSize()[0] - 2
    #记录开始时间
    th.start_time = time.time()
    msg = '[+] Set the number of thread: %d' % th.thread_num
    outputscreen.success(msg)

def scan():
    while True:
        #协程模式
        if th.target.qsize() > 0 and th.is_continue:
            target = str(th.target.get(timeout=1.0))
        else:
            break
        try:
            #对每个target进行检测
            bruter(target)
        except Exception:
            #抛出异常时，添加errmsg键值
            th.errmsg = traceback.format_exc()
            th.is_continue = False

def run():
    initEngine()
    # Coroutine mode
    outputscreen.success('[+] Coroutine mode')
    gevent.joinall([gevent.spawn(scan) for i in range(0, th.thread_num)])
    if 'errmsg' in th:
        outputscreen.error(th.errmsg)

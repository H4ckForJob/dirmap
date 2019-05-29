#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: ttttmr
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-05-29 16:52:42
'''

import imp
import os
import queue
import sys
import time
import ipaddress

from lib.controller.bruter import loadConf
from lib.core.common import parseTarget, outputscreen
from lib.core.data import conf, paths
from thirdlib.IPy.IPy import IP

def initOptions(args):
    EngineRegister(args)
    BruterRegister(args)
    TargetRegister(args)


def EngineRegister(args):
    """
    加载并发引擎模块
    """
    conf.engine_mode = 'coroutine'

    #设置线程数
    if args.thread_num > 200 or args.thread_num < 1:
        msg = '[*] Invalid input in [-t](range: 1 to 200), has changed to default(30)'
        outputscreen.warning(msg)
        conf.thread_num = 30
        return
    conf.thread_num = args.thread_num

def BruterRegister(args):
    """
    配置bruter模块
    """

    if args.load_config_file:
        #加载配置文件
        loadConf()
    else:
        outputscreen.error("[+] Function development, coming soon!please use -lcf parameter")
        if args.debug:
            conf.debug = args.debug
        else:
            conf.debug = args.debug
        sys.exit()

def TargetRegister(args):
    """
    加载目标模块
    """
    msg = '[*] Initialize targets...'
    outputscreen.warning(msg)

    #初始化目标队列
    conf.target = queue.Queue()

    # 用户输入入队
    if args.target_input:
        # 尝试解析目标地址
        try:
            lists=parseTarget(args.target_input)
        except:
            helpmsg = "Invalid input in [-i], Example: -i [http://]target.com or 192.168.1.1[/24] or 192.168.1.1-192.168.1.100"
            outputscreen.error(helpmsg)
            sys.exit()
        # 判断处理量
        if (len(lists))>100000:
            warnmsg = "[*] Loading %d targets, Maybe it's too much, continue? [y/N]" % (len(lists))
            outputscreen.warning(warnmsg)
            flag =input()
            if flag in ('Y', 'y', 'yes', 'YES','Yes'):
                pass
            else:
                msg = '[-] User quit!'
                outputscreen.warning(msg)
                sys.exit()
        msg = '[+] Load targets from: %s' % args.target_input
        outputscreen.success(msg)
        # save to conf
        for target in lists:
            conf.target.put(target)
        conf.target_nums = conf.target.qsize()

    # 文件读入入队
    elif args.target_file:
        if not os.path.isfile(args.target_file):
            msg = '[-] TargetFile not found: %s' % args.target_file
            outputscreen.error(msg)
            sys.exit()
        msg = '[+] Load targets from: %s' % args.target_file
        outputscreen.success(msg)
        with open(args.target_file, 'r', encoding='utf-8') as f:
            targets = f.readlines()
            for target in targets:
                target=target.strip('\n')
                parsed_target=parseTarget(target)
                for i in parsed_target:
                    conf.target.put(i)
        conf.target_nums = conf.target.qsize()

    #验证目标数量
    if conf.target.qsize() == 0:
        errormsg = msg = '[!] No targets found.Please load targets with [-i|-iF]'
        outputscreen.error(errormsg)
        sys.exit()
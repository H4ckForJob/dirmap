#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-04-12 21:58:42
'''

import imp
import os
import queue
import sys
import time

from lib.controller.bruter import loadConf
from lib.core.common import genIP, outputscreen
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

    #单目标入队
    if args.target_single:
        msg = '[+] Load target: %s' % args.target_single
        outputscreen.success(msg)
        conf.target.put(args.target_single)

    #多目标入队
    elif args.target_file:
        if not os.path.isfile(args.target_file):
            msg = '[-] TargetFile not found: %s' % args.target_file
            outputscreen.error(msg)
            sys.exit()
        msg = '[+] Load targets from: %s' % args.target_file
        outputscreen.success(msg)
        with open(args.target_file, 'r', encoding='utf8') as f:
            targets = f.readlines()
            for target in targets:
                conf.target.put(target.strip('\n'))

    #ip范围目标入队.e.g. 192.168.1.1-192.168.1.100
    elif args.target_range:
        try:
            lists = genIP(args.target_range)
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
            
            msg = '[+] Load targets from: %s' % args.target_range
            outputscreen.success(msg)

            # save to conf
            for target in lists:
                conf.target.put(target)
        except:
            helpmsg = "Invalid input in [-iR], Example: -iR 192.168.1.1-192.168.1.100"
            outputscreen.error(helpmsg)
            sys.exit()
    
    # ip/mask e.g. 192.168.1.2/24
    elif args.target_network: 
        try:
            # get 192.168.1.2 -->192.168.1.0
            ip_format= args.target_network.split('/')
            ip_str = IP(ip_format[0]).strBin()
            ip_str = ip_str[0:int(ip_format[1])]+'0'*(32-int(ip_format[1])) 
            ip = "%s.%s.%s.%s"%(str(int(ip_str[0:8],2)), str(int(ip_str[8:16],2)), str(int(ip_str[16:24],2)), str(int(ip_str[24:32],2)))
            
            ip_range = IP('%s/%s'%(ip,ip_format[1]))
            
            msg = '[+] Load targets from: %s' % args.target_network
            outputscreen.success(msg)
            
            for i in ip_range:
                conf.target.put(i)
        except:
            msg = "[-] Invalid input in [-iN], Example: -iN 192.168.1.0/24"
            outputscreen.error(msg)
            sys.exit()
            

        
    #验证目标数量
    if conf.target.qsize() == 0:
        errormsg = msg = 'No targets found\nPlease load targets with [-iU|-iF|-iR|-iN] or use API with [-aZ|-aS|-aG|-aF]'
        outputscreen.error(errormsg)
        sys.exit()

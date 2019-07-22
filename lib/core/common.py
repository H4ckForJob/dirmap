#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: ttttmr
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-05-29 16:49:22
'''

import os.path
import sys
import urllib
import ipaddress
import re

from lib.core.data import cmdLineOptions, conf, paths, payloads
from lib.core.enums import COLOR
from lib.core.setting import BANNER
from thirdlib.colorama import Back, Fore, Style, init

init(autoreset=True)
class Outputscreen:
    """
    显示颜色类
    """
    def info(self, s):
        print(Style.BRIGHT+Fore.WHITE + str(s) + Fore.RESET+Style.RESET_ALL)

    def success(self, s):
        print(Style.BRIGHT+Fore.GREEN + str(s) + Fore.RESET+Style.RESET_ALL)

    def warning(self, s):
        print(Style.BRIGHT+Fore.CYAN + str(s) + Fore.RESET+Style.RESET_ALL)

    def error(self, s):
        print(Style.BRIGHT+Fore.RED + str(s) + Fore.RESET+Style.RESET_ALL)

    # for banner
    def blue(self, s):
        print(Style.BRIGHT+Fore.BLUE + str(s) + Fore.RESET+Style.RESET_ALL)

#创建outputscreen对象，用于输出各种颜色的信息
outputscreen=Outputscreen()

def setPaths():
    """
    设置全局绝对路径
    """
    # 根目录
    root_path = paths.ROOT_PATH
    # datapath
    paths.DATA_PATH = os.path.join(root_path, "data")
    paths.OUTPUT_PATH = os.path.join(root_path, "output")
    paths.CONFIG_PATH = os.path.join(root_path, "dirmap.conf")
    if not os.path.exists(paths.OUTPUT_PATH):
        os.mkdir(paths.OUTPUT_PATH)
    if not os.path.exists(paths.DATA_PATH):
        os.mkdir(paths.DATA_PATH)

    # paths.WEAK_PASS = os.path.join(paths.DATA_PATH, "pass100.txt")
    # paths.LARGE_WEAK_PASS = os.path.join(paths.DATA_PATH, "pass1000.txt")
    # paths.UA_LIST_PATH = os.path.join(paths.DATA_PATH, "user-agents.txt")

    if os.path.isfile(paths.CONFIG_PATH):
        pass
    else:
        msg = 'Config files missing, it may cause an issue.\n'
        outputscreen.error(msg)
        sys.exit(0)

    #print(root_path,paths.DATA_PATH,paths.SCRIPT_PATH,paths.OUTPUT_PATH,paths.CONFIG_PATH)
    #print(paths.WEAK_PASS,paths.LARGE_WEAK_PASS,paths.UA_LIST_PATH)

def banner():
    '''
    @description: 打印banner
    @param {type}
    @return:
    '''
    outputscreen.blue(BANNER)

# 将'192.168.1.1-192.168.1.100'分解成ip地址列表
def genIP(ip_range):
    '''
    print (genIP('192.18.1.1-192.168.1.3'))
    ['192.168.1.1', '192.168.1.2', '192.168.1.3']
    '''
    # from https://segmentfault.com/a/1190000010324211
    def num2ip (num):
        return '%s.%s.%s.%s' % ((num >> 24) & 0xff, (num >> 16) & 0xff, (num >> 8) & 0xff, (num & 0xff))

    def ip2num(ip):
        ips = [int(x) for x in ip.split('.')]
        return ips[0]<< 24 | ips[1]<< 16 | ips[2] << 8 | ips[3]

    start ,end = [ip2num(x) for x in ip_range.split('-')]
    return [num2ip(num) for num in range(start,end+1) if num & 0xff]

# 识别目标，转换成列表形式
def parseTarget(target):
    lists=[]
    ipv4withmask_re=re.compile("^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])/(3[0-2]|[1-2]?[0-9])$")
    ipv4range_re=re.compile("^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])-(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$")
    try:
        # 尝试解析url
        parsed_url=urllib.parse.urlparse(target)
        # 判断不带http
        if parsed_url.scheme != 'http':
            # 判断IP/Mask格式
            if ipv4withmask_re.search(parsed_url.path):
                # 是子网还是网址 e.g. 192.168.1.1/24 or http://192.168.1.1/24
                infomsg = "[*] %s is IP/Mask[Y] or URL(http://)[n]? [Y/n]" %target
                outputscreen.info(infomsg)
                flag =input()
                if flag in ('N', 'n', 'no', 'No', 'NO'):
                    # 按链接处理 e.g. http://192.168.1.1/24
                    lists.append(target)
                else:
                    # 按子网处理 e.g. 192.168.1.1/24
                    lists=list(ipaddress.ip_interface(target).network)
            # 判断网络范围格式 e.g. 192.168.1.1-192.168.1.100
            elif ipv4range_re.search(target):
                lists=genIP(target)
            # 按照链接处理
            else:
                lists.append(target)
        # 为http://格式
        else:
            lists.append(target)
    except:
        # 识别失败
        pass
    return lists

def intToSize(bytes):
    '''
    @description: bits大小转换，对人类友好
    @param {type}
    @return:
    '''
    b = 1024 * 1024 * 1024 * 1024
    a = ['t','g','m','k','']
    for i in a:
        if bytes >= b:
            return '%.2f%sb' % (float(bytes) / float(b), i)
        b /= 1024
    return '0b'

def urlSimilarCheck(url):
    '''
    @description: url相似度分析，当url路径和参数键值类似时，则判为重复，参考某人爬虫
    @param {type}
    @return: 非重复返回True
    '''
    url_struct = urllib.parse.urlparse(url)
    query_key = '|'.join(sorted([i.split('=')[0] for i in url_struct.query.split('&')]))
    url_hash = hash(url_struct.path + query_key)
    if url_hash not in payloads.similar_urls_set:
        payloads.similar_urls_set.add(url_hash)
        return True
    return False

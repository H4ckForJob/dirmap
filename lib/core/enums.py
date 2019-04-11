#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: xxlin
@Date: 2019-04-10 13:27:58
@LastEditTime: 2019-04-11 11:40:38
'''

class COLOR:
    black = 30  #  黑色
    red = 31  #  红色
    green = 32  #  绿色
    yellow = 33  #  黄色
    blue = 34  #  蓝色
    purple = 35  #  紫红色
    cyan = 36  #  青蓝色
    white = 37  #  白色
    
class BRUTER_RESULT_STATUS:
    FAIL = 0
    SUCCESS = 1
    RETRAY = 2

class PROXY_TYPE:  # keep same with SocksiPy(import socks)
    PROXY_TYPE_SOCKS4 = SOCKS4 = 1
    PROXY_TYPE_SOCKS5 = SOCKS5 = 2
    PROXY_TYPE_HTTP = HTTP = 3
    PROXY_TYPE_HTTP_NO_TUNNEL = 4
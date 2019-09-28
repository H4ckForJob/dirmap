#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@Author: xxlin
@LastEditors: ttttmr
@Date: 2019-03-14 09:49:05
@LastEditTime: 2019-09-08 12:34:26
'''

import configparser
import hashlib
import os
import random
import re
import sys
import time
import urllib

import gevent
import progressbar
import requests
from gevent.queue import Queue
from lxml import etree

from lib.core.common import intToSize, outputscreen, urlSimilarCheck
from lib.core.data import bar, conf, paths, payloads, tasks, th
from lib.utils.config import ConfigFileParser
from lib.plugins.inspector import Inspector

#防止ssl未校验时出现提示信息
requests.packages.urllib3.disable_warnings()

#dict_mode的payloads
payloads.dict_mode_dict = set()
#crawl_mode的payloads
payloads.crawl_mode_dynamic_fuzz_temp_dict = set()
payloads.similar_urls_set = set()
payloads.crawl_mode_dynamic_fuzz_dict = list()
#blast_mode的payload
payloads.blast_mode_custom_charset_dict = list()
#fuzz_mode的payload
payloads.fuzz_mode_dict = list()

#创建all_tasks队列
tasks.all_task = Queue()
tasks.task_length = 0
tasks.task_count = 0

#创建crawl_tasks队列
tasks.crawl_task = Queue()

#假性404页面md5列表
conf.autodiscriminator_md5 = set()

bar.log = progressbar.ProgressBar()

def saveResults(domain,msg):
    '''
    @description: 结果保存，以"域名.txt"命名，url去重复
    @param {domain:域名,msg:保存的信息}
    @return: null
    '''
    filename = domain +'.txt'
    conf.output_path = os.path.join(paths.OUTPUT_PATH, filename)
    #判断文件是否存在，若不存在则创建该文件
    if not os.path.exists(conf.output_path):
        with open(conf.output_path,'w+') as temp:
            pass
    with open(conf.output_path,'r+') as result_file:
        old = result_file.read()
        if msg+'\n' in old:
            pass
        else:
            result_file.write(msg+'\n')

def loadConf():
    '''
    @description: 加载扫描配置(以后将使用参数，而非从文件加载)
    @param {type}
    @return:
    '''

    conf.recursive_scan = eval(ConfigFileParser().recursive_scan())
    conf.recursive_scan_max_url_length = eval(ConfigFileParser().recursive_scan_max_url_length())
    conf.recursive_status_code = eval(ConfigFileParser().recursive_status_code())
    conf.recursive_blacklist_exts = eval(ConfigFileParser().recursive_blacklist_exts())
    conf.exclude_subdirs = eval(ConfigFileParser().exclude_subdirs())

    conf.dict_mode = eval(ConfigFileParser().dict_mode())
    conf.dict_mode_load_single_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().dict_mode_load_single_dict()))
    conf.dict_mode_load_mult_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().dict_mode_load_mult_dict()))
    conf.blast_mode = eval(ConfigFileParser().blast_mode())
    conf.blast_mode_min = eval(ConfigFileParser().blast_mode_min())
    conf.blast_mode_max = eval(ConfigFileParser().blast_mode_max())
    conf.blast_mode_az = eval(ConfigFileParser().blast_mode_az())
    conf.blast_mode_num = eval(ConfigFileParser().blast_mode_num())
    conf.blast_mode_custom_charset = eval(ConfigFileParser().blast_mode_custom_charset())
    conf.blast_mode_resume_charset = eval(ConfigFileParser().blast_mode_resume_charset())
    conf.crawl_mode = eval(ConfigFileParser().crawl_mode())
    conf.crawl_mode_dynamic_fuzz_suffix = eval(ConfigFileParser().crawl_mode_dynamic_fuzz_suffix())
    conf.crawl_mode_parse_robots = eval(ConfigFileParser().crawl_mode_parse_robots())
    conf.crawl_mode_parse_html = eval(ConfigFileParser().crawl_mode_parse_html())
    conf.crawl_mode_dynamic_fuzz = eval(ConfigFileParser().crawl_mode_dynamic_fuzz())
    conf.fuzz_mode = eval(ConfigFileParser().fuzz_mode())
    conf.fuzz_mode_load_single_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().fuzz_mode_load_single_dict()))
    conf.fuzz_mode_load_mult_dict = os.path.join(paths.DATA_PATH,eval(ConfigFileParser().fuzz_mode_load_mult_dict()))
    conf.fuzz_mode_label = eval(ConfigFileParser().fuzz_mode_label())

    conf.request_headers = eval(ConfigFileParser().request_headers())
    conf.request_header_ua = eval(ConfigFileParser().request_header_ua())
    conf.request_header_cookie = eval(ConfigFileParser().request_header_cookie())
    conf.request_header_401_auth = eval(ConfigFileParser().request_header_401_auth())
    conf.request_timeout = eval(ConfigFileParser().request_timeout())
    conf.request_delay = eval(ConfigFileParser().request_delay())
    conf.request_limit = eval(ConfigFileParser().request_limit())
    conf.request_max_retries = eval(ConfigFileParser().request_max_retries())
    conf.request_persistent_connect = eval(ConfigFileParser().request_persistent_connect())
    conf.request_method = eval(ConfigFileParser().request_method())
    conf.redirection_302 = eval(ConfigFileParser().redirection_302())
    conf.file_extension = eval(ConfigFileParser().file_extension())

    conf.response_status_code = eval(ConfigFileParser().response_status_code())
    conf.response_header_content_type = eval(ConfigFileParser().response_header_content_type())
    conf.response_size = eval(ConfigFileParser().response_size())
    conf.auto_check_404_page = eval(ConfigFileParser().auto_check_404_page())
    conf.custom_503_page = eval(ConfigFileParser().custom_503_page())
    conf.custom_response_page = eval(ConfigFileParser().custom_response_page())
    conf.skip_size = eval(ConfigFileParser().skip_size())

    conf.proxy_server = eval(ConfigFileParser().proxy_server())

    conf.debug = eval(ConfigFileParser().debug())
    conf.update = eval(ConfigFileParser().update())

def recursiveScan(response_url,all_payloads):
    '''
    @description: 检测出一级目录后，一级目录后遍历添加所有payload，继续检测
    @param {type}
    @return:
    '''
    if not conf.recursive_scan:
        return
    # 当前url后缀在黑名单内，不进行递归
    if response_url.split('.')[-1].lower() in conf.recursive_blacklist_exts:
        return
    #XXX:payloads字典要固定格式
    for payload in all_payloads:
        #判断是否排除。若在排除的目录列表中，则排除。self.excludeSubdirs排除的列表，配置文件中，形如:/test、/test1
        if payload in [directory for directory in conf.exclude_subdirs]:
            return
        #payload拼接，处理/重复或缺失
        if response_url.endswith('/') and payload.startswith('/'):
            # /重复，url和payload都有/，删去payload的/前缀
            payload = payload[1:]
        elif (not response_url.endswith('/')) and (not payload.startswith('/')):
            # /缺失，url和payload都不包含/，在payload前追加/
            payload = '/'+payload
        #拼接payload，限制url长度，入队tasks
        newpayload=response_url+payload
        if(len(newpayload) < int(conf.recursive_scan_max_url_length)):
            tasks.all_task.put(response_url + payload)

def loadSingleDict(path):
    '''
    @description: 添加单个字典文件
    @param {path:字典文件路径}
    @return:
    '''
    try:
        outputscreen.success('[+] Load dict:{}'.format(path))
        #加载文件时，使用utf-8编码，防止出现编码问题
        with open(path,encoding='utf-8') as single_file:
            return single_file.read().splitlines()
    except Exception as e:
        outputscreen.error('[x] plz check file path!\n[x] error:{}'.format(e))
        sys.exit()

def loadMultDict(path):
    '''
    @description: 添加多个字典文件
    @param {path:字典文件路径}
    @return:
    '''
    tmp_list = []
    try:
        for file in os.listdir(path):
            #FIXME:这里解决dict和fuzz模式加载多字典问题，但是loadMultDict变得臃肿，后期需要处理
            if conf.dict_mode and conf.fuzz_mode:
                outputscreen.error('[x] Can not use dict and fuzz mode at the same time!')
                sys.exit()
            if conf.dict_mode == 2:
                tmp_list.extend(loadSingleDict(os.path.join(conf.dict_mode_load_mult_dict,file)))
            if conf.fuzz_mode == 2:
                tmp_list.extend(loadSingleDict(os.path.join(conf.fuzz_mode_load_mult_dict,file)))
        return tmp_list
    except  Exception as e:
        outputscreen.error('[x] plz check file path!\n[x] error:{}'.format(e))
        sys.exit()

def loadSuffix(path):
    '''
    @description: 添加动态爬虫字典后缀规则
    @param {type}
    @return:
    '''
    try:
        with open(path) as f:
            #要去掉#开头的字典
            payloads.suffix = set(f.read().split('\n')) - {'', '#'}
    except  Exception as e:
        outputscreen.error('[x] plz check file path!\n[x] error:{}'.format(e))
        sys.exit()

def generateCrawlDict(base_url):
    '''
    @description: 生成动态爬虫字典
    @param {base_url:}
    @return:
    '''
    def _splitFilename(filename):

        full_filename = filename.rstrip('.')
        extension = full_filename.split('.')[-1]
        name = '.'.join(full_filename.split('.')[:-1])

        return name, extension

    url = base_url.split('?')[0].rstrip('/')
    if not urllib.parse.urlparse(url).path:
        return list()

    path = '/'.join(url.split('/')[:-1])
    filename = url.split('/')[-1]

    # Check if target CMS uses route instead of static file
    isfile = True if '.' in filename else False

    if isfile:
        name, extension = _splitFilename(filename)

    final_urls = list()
    for each in payloads.suffix:
        new_filename = path + '/' + each.replace('{FULL}', filename)
        if isfile:
            new_filename = new_filename.replace('{NAME}', name).replace('{EXT}', extension)
        else:
            if '{NAME}' in each or '{EXT}' in each:
                continue
        final_urls.append(urllib.parse.urlparse(new_filename.replace('..', '.')).path)

    return final_urls

def generateBlastDict():
    '''
    @description: 生成纯暴力字典，支持断点续生成
    @param {type}
    @return:
    '''
    the_min = conf.blast_mode_min
    if conf.blast_mode_resume_charset != '':
        the_min = len(conf.blast_mode_resume_charset)
        if conf.blast_mode_min > the_min or conf.blast_mode_max < the_min:
            outputscreen.error('[+] Invalid resume length: %d\n\n' % the_min)
            the_min = conf.blast_mode_min
            conf.blast_mode_resume_charset = ''
    for length in range(the_min, conf.blast_mode_max + 1):
        generateLengthDict(length)
        conf.blast_mode_resume_charset = ''
    return payloads.blast_mode_custom_charset_dict

def generateLengthDict(length):
    '''
    @description: 生成length长度的字典
    @param {type}
    @return:
    '''
    lst = [0] * length
    if len(conf.blast_mode_resume_charset) == length and conf.blast_mode_resume_charset != '':
        #enumerate()用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
        for i, letter in enumerate(conf.blast_mode_resume_charset):
            if conf.blast_mode_custom_charset.find(letter) == -1:
                outputscreen.error('[+] Invalid resume string: "%s"\n\n' % conf.blast_mode_resume_charset)
                lst = [0] * length
                break
            lst[i] = conf.blast_mode_custom_charset.find(letter)
    lines_max = 1
    for l in lst:
        lines_max *= (len(conf.blast_mode_custom_charset) - l)
    i = length - 1
    print_it = True
    while i >= 0:
        if print_it:
            temp = ''
            for j in lst:
                temp += conf.blast_mode_custom_charset[j]
            payloads.blast_mode_custom_charset_dict.append(temp)
            print_it = False
        lst[i] += 1
        if lst[i] >= len(conf.blast_mode_custom_charset):
            lst[i] = 0
            i -= 1
        else:
            i = length - 1
            print_it = True

def generateSingleFuzzDict(path):
    '''
    @description: 单字典。生成fuzz字典
    @param {type}
    @return:
    '''
    fuzz_path = urllib.parse.urlparse(conf.url).path
    #替换label进行fuzz字典生成
    if conf.fuzz_mode_label in fuzz_path:
        for i in loadSingleDict(path):
            payloads.fuzz_mode_dict.append(fuzz_path.replace(conf.fuzz_mode_label,i))
        return payloads.fuzz_mode_dict

def generateMultFuzzDict(path):
    '''
    @description: 多字典。生成fuzz字典
    @param {type}
    @return:
    '''
    fuzz_path = urllib.parse.urlparse(conf.url).path
    #替换label进行fuzz字典生成
    if conf.fuzz_mode_label in fuzz_path:
        for i in loadMultDict(path):
            payloads.fuzz_mode_dict.append(fuzz_path.replace(conf.fuzz_mode_label,i))
        return payloads.fuzz_mode_dict

def scanModeHandler():
    '''
    @description: 扫描模式处理，加载payloads
    @param {type}
    @return:
    '''
    if conf.recursive_scan:
        msg = '[*] Use recursive scan: Yes'
        outputscreen.warning('\r'+msg+' '*(th.console_width-len(msg)+1))
    else:
        msg = '[*] Use recursive scan: No'
        outputscreen.warning('\r'+msg+' '*(th.console_width-len(msg)+1))
    payloadlists=[]
    # fuzz模式处理，只能单独加载
    if conf.fuzz_mode:
        outputscreen.warning('[*] Use fuzz mode')
        if conf.fuzz_mode == 1:
            return generateSingleFuzzDict(conf.fuzz_mode_load_single_dict)
        if conf.fuzz_mode == 2:
            return generateMultFuzzDict(conf.fuzz_mode_load_mult_dict)
    # 其他模式处理，可同时加载
    else:
        if conf.dict_mode:
            outputscreen.warning('[*] Use dict mode')
            if conf.dict_mode == 1:
                payloadlists.extend(loadSingleDict(conf.dict_mode_load_single_dict))
            elif conf.dict_mode == 2:
                payloadlists.extend(loadMultDict(conf.dict_mode_load_mult_dict))
            else:
                outputscreen.error("[-] You must select a dict")
                sys.exit()
        if conf.blast_mode:
            outputscreen.warning('[*] Use blast mode')
            outputscreen.warning('[*] Use char set: {}'.format(conf.blast_mode_custom_charset))
            outputscreen.warning('[*] Use paylaod min length: {}'.format(conf.blast_mode_min))
            outputscreen.warning('[*] Use paylaod max length: {}'.format(conf.blast_mode_max))
            payloadlists.extend(generateBlastDict())
        #TODO:递归爬取url
        if conf.crawl_mode:
            outputscreen.warning('[*] Use crawl mode')
            #自定义header
            headers = {}
            if conf.request_headers:
                try:
                    for header in conf.request_headers.split(','):
                        k, v = header.split('=')
                        #print(k,v)
                        headers[k] = v
                except Exception as e:
                    outputscreen.error("[x] Check personalized headers format: header=value,header=value.\n[x] error:{}".format(e))
                    # sys.exit()
            #自定义ua
            if conf.request_header_ua:
                headers['User-Agent'] = conf.request_header_ua
            #自定义cookie
            if conf.request_header_cookie:
                headers['Cookie'] = conf.request_header_cookie
            try:
                response = requests.get(conf.url, headers=headers, timeout=conf.request_timeout, verify=False, allow_redirects=conf.redirection_302, proxies=conf.proxy_server)
                #获取页面url
                if (response.status_code in conf.response_status_code) and response.text:
                    html = etree.HTML(response.text)
                    #加载自定义xpath用于解析html
                    urls = html.xpath(conf.crawl_mode_parse_html)
                    for url in urls:
                        #去除相似url
                        if urlSimilarCheck(url):
                            #判断:1.是否同域名 2.netloc是否为空(值空时为同域)。若满足1或2，则添加到temp payload
                            if (urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(conf.url).netloc) or urllib.parse.urlparse(url).netloc == '':
                                payloads.crawl_mode_dynamic_fuzz_temp_dict.add(url)
                payloads.crawl_mode_dynamic_fuzz_temp_dict = payloads.crawl_mode_dynamic_fuzz_temp_dict - {'#', ''}
                if conf.crawl_mode_dynamic_fuzz:
                    #加载动态fuzz后缀，TODO:独立动态生成字典模块
                    loadSuffix(os.path.join(paths.DATA_PATH,conf.crawl_mode_dynamic_fuzz_suffix))
                    #生成新爬虫动态字典
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.extend(generateCrawlDict(i))
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.append(urllib.parse.urlparse(i).path)
                    payloadlists.extend(set(payloads.crawl_mode_dynamic_fuzz_dict))
                else:
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.append(urllib.parse.urlparse(i).path)
                    payloadlists.extend(set(payloads.crawl_mode_dynamic_fuzz_dict))
            except requests.exceptions.ConnectionError as e:
                outputscreen.error("[x] Crawler network connection error!plz check whether the target is accessible")
                # sys.exit()

    if payloadlists:
        return payloadlists
    else:
        outputscreen.error("[-] You have to select at least one mode , plz check mode config")
        sys.exit()

def responseHandler(response):
    '''
    @description: 处理响应结果
    @param {type}
    @return:
    '''
    #结果处理阶段
    try:
        size = intToSize(int(response.headers['content-length']))
    except (KeyError, ValueError):
        size = intToSize(len(response.content))
    #跳过大小为skip_size的页面
    if size == conf.skip_size:
        return

    #自动识别404-判断是否与获取404页面特征匹配
    if conf.auto_check_404_page:
        if hashlib.md5(response.content).hexdigest() in conf.autodiscriminator_md5:
            return

    #自定义状态码显示
    if response.status_code in conf.response_status_code:
        msg = '[{}]'.format(str(response.status_code))
        if conf.response_header_content_type:
            msg += '[{}]'.format(response.headers.get('content-type'))
        if conf.response_size:
            msg += '[{}] '.format(str(size))
        msg += response.url
        outputscreen.info('\r'+msg+' '*(th.console_width-len(msg)+1))
        conf['thread'].update.emit(response.url,response.headers.get('content-type'),str(size),str(response.status_code))
        #已去重复，结果保存。NOTE:此处使用response.url进行文件名构造，解决使用-iL参数时，不能按照域名来命名文件名的问题
        #使用replace()，替换`:`，修复window下不能创建有`:`的文件问题
        saveResults(urllib.parse.urlparse(response.url).netloc.replace(':','_'),msg)
    #关于递归扫描。响应在自定义状态码中时，添加判断是否进行递归扫描
    if response.status_code in conf.recursive_status_code:
        if conf.recursive_scan:
            recursiveScan(response.url,payloads.all_payloads)

    #自定义正则匹配响应
    if conf.custom_response_page:
        pattern = re.compile(conf.custom_response_page)
        if pattern.search(response.text):
            outputscreen.info('[!] Custom response information matched\n[!] use regular expression:{}\n[!] matched page:{}'.format(conf.custom_response_page,response.text))

def worker():
    '''
    @description: 封包发包穷举器
    @param {type}
    @return:
    '''
    payloads.current_payload = tasks.all_task.get()
    #1自定义封包阶段
    #自定义header
    headers = {}
    if conf.request_headers:
        try:
            for header in conf.request_headers.split(','):
                k, v = header.split('=')
                #print(k,v)
                headers[k] = v
        except Exception as e:
            outputscreen.error("[x] Check personalized headers format: header=value,header=value.\n[x] error:{}".format(e))
            sys.exit()
    #自定义ua
    if conf.request_header_ua:
        headers['User-Agent'] = conf.request_header_ua
    #自定义cookie
    if conf.request_header_cookie:
        headers['Cookie'] = conf.request_header_cookie

    try:
        #2进入发送请求流程
        #延迟请求
        if conf.request_delay:
            random_sleep_second = random.randint(0,abs(conf.request_delay))
            time.sleep(random_sleep_second)

        response = requests.request(conf.request_method, payloads.current_payload, headers=headers, timeout=conf.request_timeout, verify=False, allow_redirects=conf.redirection_302, proxies=conf.proxy_server)
        #3进入结果处理流程
        responseHandler(response)
    except requests.exceptions.Timeout as e:
        #outputscreen.error('[x] timeout! url:{}'.format(payloads.current_payload))
        pass
    except Exception as e:
        # outputscreen.error('[x] error:{}'.format(e))
        pass
    finally:
        #更新进度条
        tasks.task_count += 1
        bar.log.update(tasks.task_count)
        conf['thread'].update_status.emit()

def boss():
    '''
    @description: worker控制器
    @param {type}
    @return:
    '''
    while not tasks.all_task.empty() and not conf.is_stop:
        worker()

def bruter(url):
    '''
    @description: 扫描插件入口函数
    @param {url:目标}
    @return:
    '''

    #url初始化
    conf.parsed_url = urllib.parse.urlparse(url)
    #填补协议
    if conf.parsed_url.scheme != 'http' and conf.parsed_url.scheme != 'https':
        url = 'http://' + url
        conf.parsed_url = urllib.parse.urlparse(url)
    #全局target的url，给crawl、fuzz模块使用。XXX:要放在填补url之前，否则fuzz模式会出现这样的问题：https://target.com/phpinfo.{dir}/
    conf.url = url
    #填补url后的/
    if not url.endswith('/'):
        url = url + '/'

    #打印当前target
    msg = '[+] Current target: {}'.format(url)
    outputscreen.success('\r'+msg+' '*(th.console_width-len(msg)+1))
    #自动识别404-预先获取404页面特征
    if conf.auto_check_404_page:
        outputscreen.warning("[*] Launching auto check 404")
        # Autodiscriminator (probably deprecated by future diagnostic subsystem)
        i = Inspector(url)
        (result, notfound_type) = i.check_this()
        if notfound_type == Inspector.TEST404_MD5 or notfound_type == Inspector.TEST404_OK:
            conf.autodiscriminator_md5.add(result)

    #加载payloads
    payloads.all_payloads = scanModeHandler()
    #FIXME:设置后缀名。当前以拼接方式实现，遍历一遍payload。
    try:
        if conf.file_extension:
            outputscreen.warning('[+] Use file extentsion: {}'.format(conf.file_extension))
            for i in range(len(payloads.all_payloads)):
                payloads.all_payloads[i] += conf.file_extension
    except:
        outputscreen.error('[+] plz check extension!')
        sys.exit()
    #debug模式，打印所有payload，并退出
    if conf.debug:
        outputscreen.blue('[+] all payloads:{}'.format(payloads.all_payloads))
        sys.exit()
    #payload入队task队列
    for payload in payloads.all_payloads:
        #FIXME:添加fuzz模式时，引入的url_payload构造判断
        if conf.fuzz_mode:
            url_payload = conf.parsed_url.scheme + '://' + conf.parsed_url.netloc + payload
        else:
            url_payload = url + payload
        #print(url_payload)
        #payload入队，等待处理
        tasks.all_task.put(url_payload)
    #设置进度条长度，若是递归模式或爬虫模式，则不设置任务队列长度，即无法显示进度，仅显示耗时
    if not conf.recursive_scan:
        #NOTE:这里取所有payloads的长度*target数量计算任务总数，修复issue#2
        tasks.task_length = len(payloads.all_payloads)*conf.target_nums
        bar.log.start(tasks.task_length)
    #FIXME:循环任务数不能一次性取完所有的task，暂时采用每次执行30个任务。这样写还能解决hub.LoopExit的bug
    while not tasks.all_task.empty():
        all_task = [gevent.spawn(boss) for i in range(conf.request_limit)]
        gevent.joinall(all_task)

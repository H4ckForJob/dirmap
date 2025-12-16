#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
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

# Prevent SSL warning messages when verification is disabled
requests.packages.urllib3.disable_warnings()

# payloads for dict_mode
payloads.dict_mode_dict = set()
# payloads for crawl_mode
payloads.crawl_mode_dynamic_fuzz_temp_dict = set()
payloads.similar_urls_set = set()
payloads.crawl_mode_dynamic_fuzz_dict = list()
# payload for blast_mode
payloads.blast_mode_custom_charset_dict = list()
# payload for fuzz_mode
payloads.fuzz_mode_dict = list()

# create all_tasks queue
tasks.all_task = Queue()
tasks.task_length = 0
tasks.task_count = 0

# create crawl_tasks queue
tasks.crawl_task = Queue()

# fake 404 page md5 list
conf.autodiscriminator_md5 = set()

bar.log = progressbar.ProgressBar()

def saveResults(domain,msg):
    '''
    @description: Save results, named as "domain.txt", deduplicate URLs
    @param {domain: domain name, msg: information to save}
    @return: null
    '''
    filename = domain +'.txt'
    conf.output_path = os.path.join(paths.OUTPUT_PATH, filename)
    # Check if file exists, create if not
    if not os.path.exists(conf.output_path):
        with open(conf.output_path,'w+') as temp:
            pass
    with open(conf.output_path,'r+') as result_file:
        old = result_file.read()
        if msg+'\n' in old:
            pass
        else:
            result_file.write(msg+'\n')

def _safe_eval(config_string):
    """
    Safely evaluate configuration values.
    Uses ast.literal_eval for security, with fallback to string values.
    """
    if not config_string:
        return ""
    try:
        return ast.literal_eval(config_string)
    except (ValueError, SyntaxError):
        return config_string

def loadConf():
    '''
    @description: Load scanning configuration (will use parameters instead of loading from file in the future)
    @param {type}
    @return:
    '''

    conf.recursive_scan = _safe_eval(ConfigFileParser().recursive_scan())
    conf.recursive_scan_max_url_length = _safe_eval(ConfigFileParser().recursive_scan_max_url_length())
    conf.recursive_status_code = _safe_eval(ConfigFileParser().recursive_status_code())
    conf.recursive_blacklist_exts = _safe_eval(ConfigFileParser().recursive_blacklist_exts())
    conf.exclude_subdirs = _safe_eval(ConfigFileParser().exclude_subdirs())

    conf.dict_mode = _safe_eval(ConfigFileParser().dict_mode())
    conf.dict_mode_load_single_dict = os.path.join(paths.DATA_PATH,_safe_eval(ConfigFileParser().dict_mode_load_single_dict()))
    conf.dict_mode_load_mult_dict = os.path.join(paths.DATA_PATH,_safe_eval(ConfigFileParser().dict_mode_load_mult_dict()))
    conf.blast_mode = _safe_eval(ConfigFileParser().blast_mode())
    conf.blast_mode_min = _safe_eval(ConfigFileParser().blast_mode_min())
    conf.blast_mode_max = _safe_eval(ConfigFileParser().blast_mode_max())
    conf.blast_mode_az = _safe_eval(ConfigFileParser().blast_mode_az())
    conf.blast_mode_num = _safe_eval(ConfigFileParser().blast_mode_num())
    conf.blast_mode_custom_charset = _safe_eval(ConfigFileParser().blast_mode_custom_charset())
    conf.blast_mode_resume_charset = _safe_eval(ConfigFileParser().blast_mode_resume_charset())
    conf.crawl_mode = _safe_eval(ConfigFileParser().crawl_mode())
    conf.crawl_mode_dynamic_fuzz_suffix = _safe_eval(ConfigFileParser().crawl_mode_dynamic_fuzz_suffix())
    conf.crawl_mode_parse_robots = _safe_eval(ConfigFileParser().crawl_mode_parse_robots())
    conf.crawl_mode_parse_html = _safe_eval(ConfigFileParser().crawl_mode_parse_html())
    conf.crawl_mode_dynamic_fuzz = _safe_eval(ConfigFileParser().crawl_mode_dynamic_fuzz())
    conf.fuzz_mode = _safe_eval(ConfigFileParser().fuzz_mode())
    conf.fuzz_mode_load_single_dict = os.path.join(paths.DATA_PATH,_safe_eval(ConfigFileParser().fuzz_mode_load_single_dict()))
    conf.fuzz_mode_load_mult_dict = os.path.join(paths.DATA_PATH,_safe_eval(ConfigFileParser().fuzz_mode_load_mult_dict()))
    conf.fuzz_mode_label = _safe_eval(ConfigFileParser().fuzz_mode_label())

    conf.request_headers = _safe_eval(ConfigFileParser().request_headers())
    conf.request_header_ua = _safe_eval(ConfigFileParser().request_header_ua())
    conf.request_header_cookie = _safe_eval(ConfigFileParser().request_header_cookie())
    conf.request_header_401_auth = _safe_eval(ConfigFileParser().request_header_401_auth())
    conf.request_timeout = _safe_eval(ConfigFileParser().request_timeout())
    conf.request_delay = _safe_eval(ConfigFileParser().request_delay())
    conf.request_limit = _safe_eval(ConfigFileParser().request_limit())
    conf.request_max_retries = _safe_eval(ConfigFileParser().request_max_retries())
    conf.request_persistent_connect = _safe_eval(ConfigFileParser().request_persistent_connect())
    conf.request_method = _safe_eval(ConfigFileParser().request_method())
    conf.redirection_302 = _safe_eval(ConfigFileParser().redirection_302())
    conf.file_extension = _safe_eval(ConfigFileParser().file_extension())

    conf.response_status_code = _safe_eval(ConfigFileParser().response_status_code())
    conf.response_header_content_type = _safe_eval(ConfigFileParser().response_header_content_type())
    conf.response_size = _safe_eval(ConfigFileParser().response_size())
    conf.auto_check_404_page = _safe_eval(ConfigFileParser().auto_check_404_page())
    conf.custom_503_page = _safe_eval(ConfigFileParser().custom_503_page())
    conf.custom_response_page = _safe_eval(ConfigFileParser().custom_response_page())
    conf.skip_size = _safe_eval(ConfigFileParser().skip_size())

    conf.proxy_server = _safe_eval(ConfigFileParser().proxy_server())

    conf.debug = _safe_eval(ConfigFileParser().debug())
    conf.update = _safe_eval(ConfigFileParser().update())

def recursiveScan(response_url,all_payloads):
    '''
    @description: After detecting first-level directories, traverse and add all payloads to continue detection
    @param {type}
    @return:
    '''
    if not conf.recursive_scan:
        return
    # Skip recursive if current URL extension is in blacklist
    if response_url.split('.')[-1].lower() in conf.recursive_blacklist_exts:
        return
    #XXX:payloads dictionary needs fixed format
    for payload in all_payloads:
        # Check if excluded. If in excluded directory list, exclude it. exclude_subdirs list format in config file: /test, /test1
        if payload in [directory for directory in conf.exclude_subdirs]:
            return
        # Use urljoin to correctly handle URL concatenation, avoiding double slash issue
        # Ensure response_url ends with /, then use urljoin
        if not response_url.endswith('/'):
            response_url = response_url + '/'
        # Use urljoin to concatenate URLs, it automatically handles slash issues
        newpayload = urllib.parse.urljoin(response_url, payload.lstrip('/'))
        if(len(newpayload) < int(conf.recursive_scan_max_url_length)):
            tasks.all_task.put(newpayload)

def loadSingleDict(path):
    '''
    @description: Load single dictionary file
    @param {path: dictionary file path}
    @return:
    '''
    try:
        outputscreen.success('[+] Load dict:{}'.format(path))
        # Use utf-8 encoding when loading files to prevent encoding issues
        with open(path,encoding='utf-8') as single_file:
            return single_file.read().splitlines()
    except Exception as e:
        outputscreen.error('[x] plz check file path!\n[x] error:{}'.format(e))
        sys.exit()

def loadMultDict(path):
    '''
    @description: Load multiple dictionary files
    @param {path: dictionary file path}
    @return:
    '''
    tmp_list = []
    try:
        for file in os.listdir(path):
            #FIXME: This solves the problem of loading multiple dictionaries in dict and fuzz modes, but makes loadMultDict bloated, needs refactoring later
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
    @description: Load dynamic crawler dictionary suffix rules
    @param {type}
    @return:
    '''
    try:
        with open(path) as f:
            # Remove dictionary entries starting with #
            payloads.suffix = set(f.read().split('\n')) - {'', '#'}
    except  Exception as e:
        outputscreen.error('[x] plz check file path!\n[x] error:{}'.format(e))
        sys.exit()

def generateCrawlDict(base_url):
    '''
    @description: Generate dynamic crawler dictionary
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
        # Use urljoin to correctly handle path concatenation, avoiding double slash issue
        # Ensure path ends with /
        if not path.endswith('/'):
            path = path + '/'
        new_filename = urllib.parse.urljoin(path, each.replace('{FULL}', filename).lstrip('/'))
        if isfile:
            new_filename = new_filename.replace('{NAME}', name).replace('{EXT}', extension)
        else:
            if '{NAME}' in each or '{EXT}' in each:
                continue
        final_urls.append(urllib.parse.urlparse(new_filename.replace('..', '.')).path)

    return final_urls

def generateBlastDict():
    '''
    @description: Generate pure brute force dictionary, supports resume generation
    @param {type}
    @return:
    '''
    if conf.blast_mode_min > conf.blast_mode_max:
        outputscreen.error("[x] The minimum length should be less than or equal to the maximum length")
        sys.exit(1)
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
    @description: Generate dictionary of specified length
    @param {type}
    @return:
    '''
    lst = [0] * length
    if len(conf.blast_mode_resume_charset) == length and conf.blast_mode_resume_charset != '':
        #enumerate() is used to combine a traversable data object (such as list, tuple or string) into an index sequence
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
    @description: Single dictionary. Generate fuzz dictionary
    @param {type}
    @return:
    '''
    fuzz_path = urllib.parse.urlparse(conf.url).path
    # Replace label to generate fuzz dictionary
    if conf.fuzz_mode_label in fuzz_path:
        for i in loadSingleDict(path):
            payloads.fuzz_mode_dict.append(fuzz_path.replace(conf.fuzz_mode_label,i))
        return payloads.fuzz_mode_dict
    else:
        outputscreen.error("[x] Please set the fuzz label")
        sys.exit(1)
def generateMultFuzzDict(path):
    '''
    @description: Multiple dictionaries. Generate fuzz dictionary
    @param {type}
    @return:
    '''
    fuzz_path = urllib.parse.urlparse(conf.url).path
    # Replace label to generate fuzz dictionary
    if conf.fuzz_mode_label in fuzz_path:
        for i in loadMultDict(path):
            payloads.fuzz_mode_dict.append(fuzz_path.replace(conf.fuzz_mode_label,i))
        return payloads.fuzz_mode_dict
    else:
        outputscreen.error("[x] Please set the fuzz label")
        sys.exit(1)

def scanModeHandler():
    '''
    @description: Handle scanning modes, load payloads
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
    # Handle fuzz mode, can only load separately
    if conf.fuzz_mode:
        outputscreen.warning('[*] Use fuzz mode')
        if conf.fuzz_mode == 1:
            return generateSingleFuzzDict(conf.fuzz_mode_load_single_dict)
        if conf.fuzz_mode == 2:
            return generateMultFuzzDict(conf.fuzz_mode_load_mult_dict)
    # Handle other modes, can load simultaneously
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
        #TODO: recursively crawl urls
        if conf.crawl_mode:
            outputscreen.warning('[*] Use crawl mode')
            # Custom header
            headers = {}
            if conf.request_headers:
                try:
                    for header in conf.request_headers.split(','):
                        key, value = header.split('=')
                        headers[key] = value
                except Exception as e:
                    outputscreen.error("[x] Check personalized headers format: header=value,header=value.\n[x] error:{}".format(e))
            # Custom UA
            if conf.request_header_ua:
                headers['User-Agent'] = conf.request_header_ua
            # Custom cookie
            if conf.request_header_cookie:
                headers['Cookie'] = conf.request_header_cookie
            try:
                response = requests.get(conf.url, headers=headers, timeout=conf.request_timeout, verify=False, allow_redirects=conf.redirection_302, proxies=conf.proxy_server)
                # Get page url
                if (response.status_code in conf.response_status_code) and response.text:
                    html = etree.HTML(response.text)
                    # Load custom xpath for parsing html
                    urls = html.xpath(conf.crawl_mode_parse_html)
                    for url in urls:
                        # Remove similar urls
                        if urlSimilarCheck(url):
                            # Check: 1. Same domain 2. Empty netloc (empty means same domain). Add to temp payload if 1 or 2 is met
                            if (urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(conf.url).netloc) or urllib.parse.urlparse(url).netloc == '':
                                payloads.crawl_mode_dynamic_fuzz_temp_dict.add(url)
                payloads.crawl_mode_dynamic_fuzz_temp_dict = payloads.crawl_mode_dynamic_fuzz_temp_dict - {'#', ''}
                if conf.crawl_mode_dynamic_fuzz:
                    # Load dynamic fuzz suffix, TODO: separate dynamic dictionary generation module
                    loadSuffix(os.path.join(paths.DATA_PATH,conf.crawl_mode_dynamic_fuzz_suffix))
                    # Generate new crawler dynamic dictionary
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.extend(generateCrawlDict(i))
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.append(urllib.parse.urlparse(i).path)
                    payloadlists.extend(set(payloads.crawl_mode_dynamic_fuzz_dict))
                else:
                    for i in payloads.crawl_mode_dynamic_fuzz_temp_dict:
                        payloads.crawl_mode_dynamic_fuzz_dict.append(urllib.parse.urlparse(i).path)
                    payloadlists.extend(set(payloads.crawl_mode_dynamic_fuzz_dict))
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
                outputscreen.error("[x] Crawler network connection error!plz check whether the target is accessible, error info:{}".format(e))

    if payloadlists:
        return payloadlists
    else:
        outputscreen.error("[-] You have to select at least one mode , plz check mode config")
        sys.exit()

def responseHandler(response):
    '''
    @description: Handle response results
    @param {type}
    @return:
    '''
    # Result processing stage
    try:
        size = intToSize(int(response.headers['content-length']))
    except (KeyError, ValueError):
        size = intToSize(len(response.content))
    # Skip pages with size equal to skip_size
    if size == conf.skip_size:
        return

    # Auto detect 404 - check if matches 404 page characteristics
    if conf.auto_check_404_page:
        if hashlib.md5(response.content).hexdigest() in conf.autodiscriminator_md5:
            return

    # Custom status code display
    if response.status_code in conf.response_status_code:
        msg = '[{}]'.format(str(response.status_code))
        if conf.response_header_content_type:
            msg += '[{}]'.format(response.headers.get('content-type'))
        if conf.response_size:
            msg += '[{}] '.format(str(size))
        msg += response.url
        if response.status_code in [200]:
            outputscreen.success('\r'+msg+' '*(th.console_width-len(msg)+1))
        elif response.status_code in [301,302]:
            outputscreen.warning('\r'+msg+' '*(th.console_width-len(msg)+1))
        elif response.status_code in [403,404]:
            outputscreen.error('\r'+msg+' '*(th.console_width-len(msg)+1))
        else:
            outputscreen.info('\r'+msg+' '*(th.console_width-len(msg)+1))
        # Already deduplicated, save results. NOTE: Using response.url to construct filename here solves the issue of not being able to name files by domain when using -iL parameter
        # Use replace() to replace `:` to fix the issue of not being able to create files with `:` on Windows
        saveResults(urllib.parse.urlparse(response.url).netloc.replace(':','_'),msg)
    # About recursive scanning. When response is in custom status codes, add check for recursive scanning
    if response.status_code in conf.recursive_status_code:
        if conf.recursive_scan:
            recursiveScan(response.url,payloads.all_payloads)

    # Custom regex response matching
    if conf.custom_response_page:
        pattern = re.compile(conf.custom_response_page)
        if pattern.search(response.text):
            outputscreen.info('[!] Custom response information matched\n[!] use regular expression:{}\n[!] matched page:{}'.format(conf.custom_response_page,response.text))

def worker():
    '''
    @description: Packet sending enumerator
    @param {type}
    @return:
    '''
    payloads.current_payload = tasks.all_task.get()
    #1 Custom packet phase
    # Custom header
    headers = {}
    if conf.request_headers:
        try:
            for header in conf.request_headers.split(','):
                key, value = header.split('=')
                headers[key] = value
        except Exception as e:
            outputscreen.error("[x] Check personalized headers format: header=value,header=value.\n[x] error:{}".format(e))
            sys.exit()
    # Custom UA
    if conf.request_header_ua:
        headers['User-Agent'] = conf.request_header_ua
    # Custom cookie
    if conf.request_header_cookie:
        headers['Cookie'] = conf.request_header_cookie

    try:
        #2 Enter request sending flow
        # Delay request
        if conf.request_delay:
            random_sleep_second = random.randint(0,abs(conf.request_delay))
            time.sleep(random_sleep_second)

        response = requests.request(conf.request_method, payloads.current_payload, headers=headers, timeout=conf.request_timeout, verify=False, allow_redirects=conf.redirection_302, proxies=conf.proxy_server)
        #3 Enter result processing flow
        responseHandler(response)
    except requests.exceptions.Timeout as e:
        #outputscreen.error('[x] timeout! url:{}'.format(payloads.current_payload))
        pass
    except Exception as e:
        # outputscreen.error('[x] error:{}'.format(e))
        pass
    finally:
        # Update progress bar
        tasks.task_count += 1
        bar.log.update(tasks.task_count)

def task_dispatcher():
    """
    Worker controller that dispatches tasks to workers.
    """
    while not tasks.all_task.empty():
        worker()

def bruter(url):
    '''
    @description: Scanning plugin entry function
    @param {url: target}
    @return:
    '''

    # URL initialization
    conf.parsed_url = urllib.parse.urlparse(url)
    # Add protocol
    if conf.parsed_url.scheme != 'http' and conf.parsed_url.scheme != 'https':
        url = 'http://' + url
        conf.parsed_url = urllib.parse.urlparse(url)
    # Global target url for crawl and fuzz modules. XXX: Must be placed before URL padding, otherwise fuzz mode will have issues like: https://target.com/phpinfo.{dir}/
    conf.url = url
    # Add trailing / to URL
    if not url.endswith('/'):
        url = url + '/'

    # Print current target
    msg = '[+] Current target: {}'.format(url)
    outputscreen.success('\r'+msg+' '*(th.console_width-len(msg)+1))
    # Auto detect 404 - pre-get 404 page characteristics
    if conf.auto_check_404_page:
        outputscreen.warning("[*] Launching auto check 404")
        # Autodiscriminator (probably deprecated by future diagnostic subsystem)
        i = Inspector(url)
        (result, notfound_type) = i.check_this()
        if notfound_type == Inspector.TEST404_MD5 or notfound_type == Inspector.TEST404_OK:
            conf.autodiscriminator_md5.add(result)

    # Load payloads
    payloads.all_payloads = scanModeHandler()
    #FIXME: Set file extensions. Currently implemented by concatenation, traverse all payloads.
    try:
        if conf.file_extension:
            outputscreen.warning('[+] Use file extentsion: {}'.format(conf.file_extension))
            for idx in range(len(payloads.all_payloads)):
                payloads.all_payloads[idx] += conf.file_extension
    except (AttributeError, TypeError) as e:
        outputscreen.error(f'[+] Please check extension configuration: {e}')
        sys.exit(1)
    # Debug mode, print all payloads and exit
    if conf.debug:
        outputscreen.blue('[+] all payloads:{}'.format(payloads.all_payloads))
        sys.exit()
    # Enqueue payloads to task queue
    for payload in payloads.all_payloads:
        #FIXME: URL payload construction check added when fuzz mode was introduced
        if conf.fuzz_mode:
            # Use urljoin to correctly handle URL concatenation, avoiding double slash issue
            base_url = conf.parsed_url.scheme + '://' + conf.parsed_url.netloc + '/'
            url_payload = urllib.parse.urljoin(base_url, payload.lstrip('/'))
        else:
            # Use urljoin to correctly handle URL concatenation, avoiding double slash issue
            url_payload = urllib.parse.urljoin(url, payload.lstrip('/'))
        # Enqueue payload, waiting for processing
        tasks.all_task.put(url_payload)
    # Set progress bar length. If recursive mode or crawler mode, do not set task queue length, i.e., cannot show progress, only show time
    if not conf.recursive_scan:
        #NOTE: Take length of all payloads * number of targets to calculate total tasks, fix issue#2
        tasks.task_length = len(payloads.all_payloads)*conf.target_nums
        bar.log.start(tasks.task_length)
    #FIXME: Cannot take all tasks at once in loop, temporarily execute 30 tasks each time. This also solves hub.LoopExit bug
    while not tasks.all_task.empty():
        all_task = [gevent.spawn(task_dispatcher) for _ in range(conf.request_limit)]
        gevent.joinall(all_task)

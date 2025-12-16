#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from configparser import ConfigParser
from lib.core.data import paths
from lib.core.common import outputscreen


class ConfigFileParser:
    @staticmethod
    def _get_option(section, option):
        try:
            cf = ConfigParser()
            cf.read(paths.CONFIG_PATH)
            return cf.get(section=section, option=option)
        except Exception as e:
            outputscreen.warning(f'Missing essential options, please check your config-file: {e}')
            return ''


    def recursive_scan(self):
        return self._get_option('RecursiveScan','conf.recursive_scan')
    def recursive_status_code(self):
        return self._get_option('RecursiveScan','conf.recursive_status_code')
    def recursive_scan_max_url_length(self):
        return self._get_option('RecursiveScan','conf.recursive_scan_max_url_length')
    def recursive_blacklist_exts(self):
        return self._get_option('RecursiveScan','conf.recursive_blacklist_exts')
    def exclude_subdirs(self):
        return self._get_option('RecursiveScan','conf.exclude_subdirs')

    def dict_mode(self):
        return self._get_option('ScanModeHandler','conf.dict_mode')
    def dict_mode_load_single_dict(self):
        return self._get_option('ScanModeHandler','conf.dict_mode_load_single_dict')
    def dict_mode_load_mult_dict(self):
        return self._get_option('ScanModeHandler','conf.dict_mode_load_mult_dict')
    def blast_mode(self):
        return self._get_option('ScanModeHandler','conf.blast_mode')
    def blast_mode_min(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_min')
    def blast_mode_max(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_max')
    def blast_mode_az(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_az')
    def blast_mode_num(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_num')
    def blast_mode_custom_charset(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_custom_charset')
    def blast_mode_resume_charset(self):
        return self._get_option('ScanModeHandler','conf.blast_mode_resume_charset')
    def crawl_mode(self):
        return self._get_option('ScanModeHandler','conf.crawl_mode')
    def crawl_mode_dynamic_fuzz_suffix(self):
        return self._get_option('ScanModeHandler','conf.crawl_mode_dynamic_fuzz_suffix')
    def crawl_mode_parse_robots(self):
        return self._get_option('ScanModeHandler','conf.crawl_mode_parse_robots')
    def crawl_mode_parse_html(self):
        return self._get_option('ScanModeHandler','conf.crawl_mode_parse_html')
    def crawl_mode_dynamic_fuzz(self):
        return self._get_option('ScanModeHandler','conf.crawl_mode_dynamic_fuzz')
    def fuzz_mode(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode')
    def fuzz_mode_load_single_dict(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode_load_single_dict')
    def fuzz_mode_load_mult_dict(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode_load_mult_dict')
    def fuzz_mode_label(self):
        return self._get_option('ScanModeHandler','conf.fuzz_mode_label')

    def request_headers(self):
        return self._get_option('RequestHandler','conf.request_headers')
    def request_header_ua(self):
        return self._get_option('RequestHandler','conf.request_header_ua')
    def request_header_cookie(self):
        return self._get_option('RequestHandler','conf.request_header_cookie')
    def request_header_401_auth(self):
        return self._get_option('RequestHandler','conf.request_header_401_auth')
    def request_timeout(self):
        return self._get_option('RequestHandler','conf.request_timeout')
    def request_delay(self):
        return self._get_option('RequestHandler','conf.request_delay')
    def request_limit(self):
        return self._get_option('RequestHandler','conf.request_limit')
    def request_max_retries(self):
        return self._get_option('RequestHandler','conf.request_max_retries')
    def request_persistent_connect(self):
        return self._get_option('RequestHandler','conf.request_persistent_connect')
    def request_method(self):
        return self._get_option('RequestHandler','conf.request_method')
    def redirection_302(self):
        return self._get_option('RequestHandler','conf.redirection_302')
    def file_extension(self):
        return self._get_option('RequestHandler','conf.file_extension')

    def response_status_code(self):
        return self._get_option('ResponseHandler','conf.response_status_code')
    def response_header_content_type(self):
        return self._get_option('ResponseHandler','conf.response_header_content_type')
    def response_size(self):
        return self._get_option('ResponseHandler','conf.response_size')
    def auto_check_404_page(self):
        return self._get_option('ResponseHandler','conf.auto_check_404_page')
    def custom_503_page(self):
        return self._get_option('ResponseHandler','conf.custom_503_page')
    def custom_response_page(self):
        return self._get_option('ResponseHandler','conf.custom_response_page')
    def skip_size(self):
        return self._get_option('ResponseHandler','conf.skip_size')

    def proxy_server(self):
        return self._get_option('ProxyHandler','conf.proxy_server')

    def debug(self):
        return self._get_option('DebugMode','conf.debug')
    def update(self):
        return self._get_option('CheckUpdate','conf.update')

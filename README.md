# Dirmap

[English](./README_EN.md)

An advanced web directory scanning tool, more powerful than DirBuster, Dirsearch, cansina, and Yu Jian

![dirmap](doc/dirmap.png)

# Requirements Analysis

After extensive research, an excellent web directory scanning tool should have at least the following features:

- Concurrent engine
- Dictionary support
- Pure brute force capability
- Page crawling for dynamic dictionary generation
- Fuzz scanning capability
- Custom requests
- Custom response result processing...

So let's take a look at Dirmap's **features**

# Features

1. Supports n targets * n payloads concurrency
2. Supports recursive scanning
3. Supports custom status codes for recursive scanning
4. Supports (single|multiple) dictionary scanning
5. Supports custom character set brute force
6. Supports crawler dynamic dictionary scanning
7. Supports custom label fuzzing for target URLs
8. Custom request User-Agent
9. Custom request random delay
10. Custom request timeout
11. Custom request proxy
12. Custom regular expression matching for fake 404 pages
13. Custom response status codes to handle
14. Custom skip pages of size x
15. Custom display content-type
16. Custom display page size
17. Deduplicate and save results by domain

# Usage

## Environment Setup

```shell
git clone <repository-url> && cd dirmap && python3 -m pip install -r requirement.txt
```

## Quick Start

### Input Target

Single target, default is http

```shell
python3 dirmap.py -i https://target.com -lcf
```

```shell
python3 dirmap.py -i 192.168.1.1 -lcf
```

Subnet (CIDR format)

```shell
python3 dirmap.py -i 192.168.1.0/24 -lcf
```

Network range

```shell
python3 dirmap.py -i 192.168.1.1-192.168.1.100 -lcf
```

### File Reading

```shell
python3 dirmap.py -iF targets.txt -lcf
```

`targets.txt` supports the above formats

### Result Saving

1. Results will be automatically saved in the `output` folder in the project root directory
2. Each target generates a txt file, named in the format `target_domain.txt`
3. Results are automatically deduplicated, no need to worry about large amounts of redundancy

## Advanced Usage

Customize dirmap configuration to explore advanced features of dirmap

Currently, configuration is done by loading configuration files, **detailed configuration via command line parameters is not supported**!

Edit `dirmap.conf` in the project root directory to configure

`dirmap.conf` Configuration Explanation

```
# Recursive scanning processing configuration
[RecursiveScan]
# Enable recursive scanning: Disabled:0; Enabled:1
conf.recursive_scan = 0
# Enable recursive scanning when encountering these status codes. Default configuration [301,403]
conf.recursive_status_code = [301,403]
# Exit scanning when URL exceeds this length
conf.recursive_scan_max_url_length = 60
# Do not recursively scan these extensions
conf.recursive_blacklist_exts = ["html",'htm','shtml','png','jpg','webp','bmp','js','css','pdf','ini','mp3','mp4']
# Set excluded scan directories. Default configuration is empty. Other configuration: e.g:['/test1','/test2']
#conf.exclude_subdirs = ['/test1','/test2']
conf.exclude_subdirs = ""

# Scanning mode processing configuration (4 modes, can only select 1 at a time)
[ScanModeHandler]
# Dictionary mode: Disabled:0; Single dictionary:1; Multiple dictionaries:2
conf.dict_mode = 1
# Path for single dictionary mode
conf.dict_mode_load_single_dict = "dict_mode_dict.txt"
# Path for multiple dictionary mode, default configuration is dictmult
conf.dict_mode_load_mult_dict = "dictmult"
# Brute force mode: Disabled:0; Enabled:1
conf.blast_mode = 0
# Minimum length for generated dictionary. Default configuration is 3
conf.blast_mode_min = 3
# Maximum length for generated dictionary. Default configuration is 3
conf.blast_mode_max = 3
# Default character set: a-z. Not yet used.
conf.blast_mode_az = "abcdefghijklmnopqrstuvwxyz"
# Default character set: 0-9. Not yet used.
conf.blast_mode_num = "0123456789"
# Custom character set. Default configuration is "abc". Use abc to construct dictionary
conf.blast_mode_custom_charset = "abc"
# Custom resume character set. Default configuration is empty.
conf.blast_mode_resume_charset = ""
# Crawler mode: Disabled:0; Enabled:1
conf.crawl_mode = 0
# Suffix dictionary for generating dynamic sensitive file payloads
conf.crawl_mode_dynamic_fuzz_suffix = "crawl_mode_suffix.txt"
# Parse robots.txt file. Not yet implemented.
conf.crawl_mode_parse_robots = 0
# Xpath expression for parsing html pages
conf.crawl_mode_parse_html = "//*/@href | //*/@src | //form/@action"
# Whether to perform dynamic crawler dictionary generation. Default configuration is 1, enable crawler dynamic dictionary generation. Other configuration: e.g: Disabled:0; Enabled:1
conf.crawl_mode_dynamic_fuzz = 1
# Fuzz mode: Disabled:0; Single dictionary:1; Multiple dictionaries:2
conf.fuzz_mode = 0
# Path for single dictionary mode.
conf.fuzz_mode_load_single_dict = "fuzz_mode_dir.txt"
# Path for multiple dictionary mode. Default configuration is: fuzzmult
conf.fuzz_mode_load_mult_dict = "fuzzmult"
# Set fuzz label. Default configuration is {dir}. Use {dir} label as dictionary insertion point, replace http://target.com/{dir}.php with http://target.com/each line in dictionary.php. Other configuration: e.g:{dir};{ext}
#conf.fuzz_mode_label = "{ext}"
conf.fuzz_mode_label = "{dir}"

# Payload processing configuration. Not yet implemented.
[PayloadHandler]

# Request processing configuration
[RequestHandler]
# Custom request headers. Default configuration is empty. Other configuration: e.g:test1=test1,test2=test2
#conf.request_headers = "test1=test1,test2=test2"
conf.request_headers = ""
# Custom request User-Agent. Default configuration is chrome's ua.
conf.request_header_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
# Custom request cookie. Default configuration is empty, no cookie set. Other configuration e.g:cookie1=cookie1; cookie2=cookie2;
#conf.request_header_cookie = "cookie1=cookie1; cookie2=cookie2"
conf.request_header_cookie = ""
# Custom 401 authentication. Not yet implemented. Because custom request header function can meet this requirement (lazy XD)
conf.request_header_401_auth = ""
# Custom request method. Default configuration is get method. Other configuration: e.g:get;head
#conf.request_method = "head"
conf.request_method = "get"
# Custom timeout for each request. Default configuration is 3 seconds.
conf.request_timeout = 3
# Random delay (0-x) seconds to send requests. Parameter must be integer. Default configuration is 0 seconds, no delay.
conf.request_delay = 0
# Custom number of request coroutine threads per target. Default configuration is 30 threads
conf.request_limit = 30
# Custom maximum retry count. Not yet implemented.
conf.request_max_retries = 1
# Set persistent connection. Whether to use session(). Not yet implemented.
conf.request_persistent_connect = 0
# 302 redirection. Default False, no redirection. Other configuration: e.g:True;False
conf.redirection_302 = False
# Add suffix after payload. Default is empty, no suffix added during scanning. Other configuration: e.g:txt;php;asp;jsp
#conf.file_extension = "txt"
conf.file_extension = ""

# Response processing configuration
[ResponseHandler]
# Set response statuses to record. Default configuration is [200], record 200 status code. Other configuration: e.g:[200,403,301]
#conf.response_status_code = [200,403,301]
conf.response_status_code = [200]
# Whether to record content-type response header. Default configuration is 1 to record
#conf.response_header_content_type = 0
conf.response_header_content_type = 1
# Whether to record page size. Default configuration is 1 to record
#conf.response_size = 0
conf.response_size = 1
# Whether to automatically detect 404 pages. Default configuration is True, enable automatic 404 detection. Other configuration reference e.g:True;False
#conf.auto_check_404_page = False
conf.auto_check_404_page = True
# Custom regular expression to match 503 pages. Not yet implemented. Feels unnecessary, might be deprecated.
#conf.custom_503_page = "page 503"
conf.custom_503_page = ""
# Custom regular expression to match page content
#conf.custom_response_page = "([0-9]){3}([a-z]){3}test"
conf.custom_response_page = ""
# Skip displaying pages of size x, if not set, please configure as "None", default configuration is "None". Other size configuration reference e.g:None;0b;1k;1m
#conf.skip_size = "0b"
conf.skip_size = "None"

# Proxy options
[ProxyHandler]
# Proxy configuration. Default is "None", no proxy enabled. Other configuration e.g:{"http":"http://127.0.0.1:8080","https":"https://127.0.0.1:8080"}
#conf.proxy_server = {"http":"http://127.0.0.1:8080","https":"https://127.0.0.1:8080"}
conf.proxy_server = None

# Debug options
[DebugMode]
# Print payloads and exit
conf.debug = 0

# Update options
[CheckUpdate]
# Get updates from github. Not yet implemented.
conf.update = 0
```

# TODO

- [x] Command line argument parsing global initialization
- [x] engine initialization
  - [x] Set thread count
- [x] target initialization
  - [x] Automatically parse and handle input format (-i,inputTarget)
    - [x] IP
    - [x] Domain
    - [x] URL
    - [x] IP/MASK
    - [x] IP Start-End
  - [x] File input (-iF,inputLocalFile)
- [ ] bruter initialization
  - [ ] Configuration loading method()
    - [ ] Read command line parameter values
    - [x] Read configuration file (-lcf,loadConfigFile)
  - [x] Recursive mode options (RecursiveScan)
    - [x] Recursive scanning (-rs,recursive_scan)
    - [x] Status codes requiring recursion (-rd,recursive_status_code)
    - [x] Exclude certain directories (-es,exclude_subdirs)
  - [ ] Scanning mode options (ScanModeHandler)
    - [x] Dictionary mode (-dm,dict_mode)
      - [x] Load single dictionary (-dmlsd,dict_mode_load_single_dict)
      - [x] Load multiple dictionaries (-dmlmd,dict_mode_load_mult_dict)
    - [ ] Brute force mode (-bm,blast_mode)
      - [x] Brute force directory length range (required)
        - [x] Minimum length (-bmmin,blast_mode_min)
        - [x] Maximum length (-bmmax,blast_mode_max)
      - [ ] Based on default character sets
        - [ ] Based on a-z
        - [ ] Based on 0-9
      - [x] Based on custom character set (-bmcc,blast_mode_custom_charset)
      - [x] Resume payload generation (-bmrc,blast_mode_resume_charset)
    - [ ] Crawler mode (-cm,crawl_mode)
      - [x] Custom parsing tags (-cmph,crawl_mode_parse_html)(a:href,img:src,form:action,script:src,iframe:src,div:src,frame:src,embed:src)
      - [ ] Parse robots.txt (-cmpr,crawl_mode_parse_robots)
      - [x] Crawler dynamic fuzz scanning (-cmdf,crawl_mode_dynamic_fuzz)
    - [x] Fuzz mode (-fm,fuzz_mode)
      - [x] Fuzz single dictionary (-fmlsd,fuzz_mode_load_single_dict)
      - [x] Fuzz multiple dictionaries (-fmlmd,fuzz_mode_load_mult_dict)
      - [x] Fuzz label (-fml,fuzz_mode_label)
  - [ ] Request optimization options (RequestHandler)
    - [x] Custom request timeout (-rt,request_timeout)
    - [x] Custom request delay (-rd,request_delay)
    - [x] Limit coroutine threads per target host (-rl,request_limit)
    - [ ] Limit retry count (-rmr,request_max_retries)
    - [ ] HTTP persistent connection (-rpc,request_persistent_connect)
    - [x] Custom request method (-rm,request_method)(get,head)
    - [x] 302 status handling (-r3,redirection_302)(whether to redirect)
    - [x] Custom header
      - [x] Custom other headers (-rh,request_headers)(solve 401 authentication)
      - [x] Custom ua (-rhua,request_header_ua)
      - [x] Custom cookie (-rhc,request_header_cookie)
  - [ ] Dictionary processing options (PayloadHandler)
    - [ ] Dictionary processing (payload modification - remove slash)
    - [ ] Dictionary processing (payload modification - add leading slash)
    - [ ] Dictionary processing (payload modification - capitalize first letter)
    - [ ] Dictionary processing (payload modification - remove extensions)
    - [ ] Dictionary processing (payload modification - remove non-alphanumeric)
  - [ ] Response result processing module (ResponseHandler)
    - [x] Response filtering (response status filtering)
    - [x] Response filtering (response header filtering)
    - [x] Response filtering (response size filtering)
    - [x] Response filtering (automatic 404 detection)
    - [x] Response filtering (custom response matching)
    - [x] Response processing (domain deduplication)
    - [x] Response processing (save results)
  - [ ] Plugin system
    - [ ] Scan plugin interface
    - [ ] Response processing plugin interface
  - [ ] Debug options
    - [x] Debug mode (-debug,debug)
  - [ ] Update options
    - [ ] Update function (-u,update)

# Star History


# Contributing

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

# Acknowledgments

Thanks to the following tools for reference:
- [DirBuster](https://sourceforge.net/projects/dirbuster/)
- [Dirsearch](https://github.com/maurosoria/dirsearch)
- [cansina](https://github.com/deibit/cansina)
- [御剑](http://www.webcache.com/soft/)
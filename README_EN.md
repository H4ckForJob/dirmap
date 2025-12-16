# Dirmap

[Chinese](./README.md)

An advanced web directory scanning tool that will be more powerful than DirBuster, Dirsearch, cansina, and Yu Jian

![dirmap](doc/dirmap.png)

# Demand analysis

After a lot of research, summarizing an excellent web directory scanning tool has at least the following features:

- Concurrency engine
- Can use the dictionary
- Can be purely blasted
- Can crawl the page dynamically to generate a dictionary
- Can fuzz scan
- Custom request
- Custom response processing...

Then take a look at the **features** of Dirmap.

# Features

1. Support n target\*n payload concurrent
2. Support recursive scanning
3. Support custom status codes that require recursive scanning
4. Support (single | multi) dictionary scan
5. Support custom character set blasting
6. Support crawler dynamic dictionary scanning
7. Support custom label fuzz target url
8. Custom Request User-Agent
9. Custom request random delay
10. Custom request timeout
11. Custom Request Broker
12. Custom Regular Expressions Match False 404 Pages
13. Customize the response status code to process
14. Customize skipping pages of size x
15. Custom display content-type
16. Customize the display page size
17. Save the results by domain name and remove duplicates

# Introduction

## Environment and download

```shell
git clone <repository-url> && cd dirmap && python3 -m pip install -r requirement.txt
```

## Quick use

### Input target

Single target, default is http

```shell
python3 dirmap.py -i https://target.com -lcf
```

```shell
python3 dirmap.py -i 192.168.1.1 -lcf
```

Subnet(CIDR format)

```shell
python3 dirmap.py -i 192.168.1.0/24 -lcf
```

Network range

```shell
python3 dirmap.py -i 192.168.1.1-192.168.1.100 -lcf
```

### Read from file

```shell
python3 dirmap.py -iF targets.txt -lcf
```

The above format is supported in `targets.txt`

### Result save

1. The result will be automatically saved in the `output` folder in the project root directory.
2. Each target generates a txt with the naming format `domain/ip.txt`
3. The result is automatically deduplicated

## Advanced

Customize the dirmap configuration and start exploring dirmap advanced features

Temporarily configure the configuration file by loading the configuration file. ** It is not supported to use the command line parameters for detailed configuration**!

Edit `dirmap.conf` in the root directory of the project to configure it.Detailed instructions for use in `dirmap.conf`

# TODO

- [x] command line parameter parsing global initialization
- [x] Cngine Initialization
  - [x] set the number of threads
- [x] Target Initialization
  - [x] automatic parsing of input formats( -i,inputTarget)
    - [x] IP
    - [x] Domain
    - [x] URL
    - [x] IP/MASK
    - [x] IP Start-End
  - [x] file reading(-iF,inputLocalFile)
- [ ] Bruter Initialization
  - [ ] Load Configuration Mode()
    - [ ] read command line parameter values
    - [x] read configuration file(-lcf,loadConfigFile)
  - [x] Recursive Mode Option(RecursiveScan)
    - [x] recursive scan (-rs, recursive_scan)
    - [x] status code requiring recursion (-rd, recursive_status_code)
    - [x] exclude certain directories (-es, exclude_subdirs)
  - [ ] Scan Mode Option (ScanModeHandler)
    - [x] dictionary mode (-dm, dict_mode)
      - [x] load a single dictionary (-dmlsd, dict_mode_load_single_dict)
      - [x] load multiple dictionaries (-dmlmd, dict_mode_load_mult_dict)
    - [ ] blast mode (-bm, blast_mode)
      - [x] blasting directory length range (required)
        - [x] minimum length (-bmmin, blast_mode_min)
        - [x] maximum length (-bmmax, blast_mode_max)
      - [ ] based on the default character set
        - [ ] based on a-z
        - [ ] based on 0-9
      - [x] based on custom character set (-bmcc, blast_mode_custom_charset)
      - [x] breakpoint resume generating payload(-bmrc, blast_mode_resume_charset)
    - [ ] crawler mode (-cm, crawl_mode)
      - [x] custom parsing tags (-cmph, crawl_mode_parse_html) (a:href, img:src, form:action,script:src,iframe:src,div:src,frame:src,embed:src)
      - [ ] parsing robots.txt (-cmpr, crawl_mode_parse_robots)
      - [x] crawler dynamic fuzz scan (-cmdf, crawl_mode_dynamic_fuzz)
    - [x] fuzz mode (-fm, fuzz_mode)
      - [x] fuzz single dictionary (-fmlsd, fuzz_mode_load_single_dict)
      - [x] fuzz multiple dictionaries (-fmlmd, fuzz_mode_load_mult_dict)
      - [x] fuzz tag (-fml, fuzz_mode_label)
  - [ ] Request Optimization Option (RequestHandler)
    - [x] custom request timeout (-rt, request_timeout)
    - [x] custom request delay (-rd, request_delay)
    - [x] limit single target host coroutine scan (-rl, request_limit)
    - [ ] limit the number of retries (-rmr, request_max_retries)
    - [ ] http persistent connection (-rpc, request_persistent_connect)
    - [x] custom request method (-rm, request_method) (get, head)
    - [x] 302 state processing (-r3, redirection_302) (redirected)
    - [x] custom header
      - [x] customize other headers (-rh, request_headers) (resolve 401 authentication required)
      - [x] custom ua(-rhua,request_header_ua)
      - [x] custom cookie (-rhc, request_header_cookie)
  - [ ] Dictionary Processing Option (PayloadHandler)
    - [ ] dictionary processing (payload modification - de-slash)
    - [ ] dictionary processing (payload modification - first character plus slash)
    - [ ] dictionary processing (payload modification - initial capitalization of words)
    - [ ] dictionary processing (payload modification - de-extension)
    - [ ] dictionary processing (payload modification - remove non-alphanumeric)
  - [ ] Response Result Processing Module (ResponseHandler)
    - [x] skips files of size x bytes (-ss, skip_size)
    - [x] automatically detect 404 pages (-ac4p, auto_check_404_page)
    - [ ] custom 503 page (-c5p, custom_503_page)
    - [ ] customize regular matching response content and perform some action
      - [x] custom regular match response (-crp, custom_response_page)
      - [ ] some operation (temporarily undefined)
    - [x] output is a custom status code (-rsc, response_status_code)
    - [x] output payload to full path (default output completion url)
    - [x] output results show content-type
    - [x] automatically repeats the results
  - [ ] Status Processing Module (StatusHandler)
    - [ ] status display (waiting for start, ongoing, paused, abnormal, completed)
    - [x] progress display
    - [ ] status control (start, pause, resume, stop)
    - [ ] continued scanning module (not yet configured)
    - [ ] breakpoint continuous sweep
    - [ ] line selection continues
  - [ ] Logging Module (ScanLogHandler)
    - [ ] scan log
    - [ ] error log
  - [ ] Proxy Module (ProxyHandler)
    - [x] single agent (-ps, proxy_server)
    - [ ] proxy pool
  - [x] Debug Mode Option (DebugMode)
    - [x] debug(--debug)
  - [ ] Check For Update Options (CheckUpdate)
    - [ ] update(--update)

# Default dictionary

The dictionary file is stored in the `data` folder in the project root directory.

1. dict_mode_dict.txt       "dictionary mode" dictionary, using `dirsearch` default dictionary
2. crawl_mode_suffix.txt    "crawler mode" dictionary, using the `FileSensor` default dictionary
3. fuzz_mode_dir.txt        "fuzz mode" dictionary, using the `DirBuster` default dictionary
4. fuzz_mode_ext.txt        "fuzz mode" dictionary, a dictionary made with common suffixes
5. dictmult                 This directory is the "dictionary mode" default multi-dictionary folder, including: BAK.min.txt (backup file small dictionary), BAK.txt (backup file large dictionary), LEAKS.txt (information leak file dictionary)
6. fuzzmult                 This directory is the default multi-dictionary folder of "fuzz mode", including: fuzz_mode_dir.txt (default directory dictionary), fuzz_mode_ext.txt (default suffix dictionary)

# Known bug

1. "crawler mode" only crawls the current page of the target and is used to generate a dynamic dictionary. The project will separate the "crawler module" from the "generate dynamic dictionary function" in the future.
2. About bruter.py line 517 `bar.log.start()` error. Solution: Please install progressbar2. Uninstall the progressbar. Prevent the import of modules of the same name. Thanks to a brother for reminding.

```shell
python3 -m pip uninstall progressbar
python3 -m pip install progressbar2
```

# Maintenance

1. If there is a problem during use, please feel free to issue an issue.
2. The project is under maintenance and new features will be added in the future. Please refer to the “TODO” list for details.

# Acknowledgement

In the process of writing dirmap, I borrowed a lot of models and ideas from excellent open source projects. I would like to express my gratitude.

- [Sqlmap](https://github.com/sqlmapproject/sqlmap)
- [POC-T](https://github.com/Xyntax/POC-T)
- [Saucerframe](https://github.com/saucer-man/saucerframe)
- [gwhatweb](https://github.com/boy-hack/gwhatweb)
- [dirsearch](https://github.com/maurosoria/dirsearch)
- [cansina](https://github.com/deibit/cansina)
- [weakfilescan](https://github.com/ring04h/weakfilescan)
- [FileSensor](https://github.com/Xyntax/FileSensor)
- [BBscan](https://github.com/lijiejie/BBScan)
- [werdy](https://github.com/derv82/werdy)

# Contact


![donate](doc/donate.jpg)
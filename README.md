# dirmap

一个高级web目录扫描工具，功能将会强于DirBuster、Dirsearch、cansina、御剑

# 需求分析

经过大量调研，总结一个优秀的web目录扫描工具至少具备以下功能：

- 能使用字典
- 能纯爆破
- 能爬取页面动态生成字典
- 能fuzz扫描...

更多内容，请参考“功能特点”

# 特别声明

dirmap在编写过程中，借鉴了大量的优秀开源项目的模式与思想，特此说明并表示感谢。

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

# 功能特点

- [x] 命令解析全局初始化
- [x] engine初始化
  - [x] 设置线程数
- [x] target初始化
  - [x] 单个url
  - [x] 多个url
  - [x] ip范围
- [ ] bruter初始化
  - [ ] 加载配置方式()
    - [ ] 读取参数值(默认)
    - [x] 读取配置文件(-lcf)
  - [ ] 递归模式选项(RecursiveScan)
    - [x] 递归扫描(-rs,recursive_scan)
    - [ ] 递归深度(-rd,recursion_depth)
    - [x] 排除某些目录(-es,exclude_subdirs)
  - [ ] 扫描模式选项(ScanModeHandler)
    - [x] 字典模式(-dm,dict_mode)
      - [x] 加载单个字典(-dmlsd,dict_mode_load_single_dict)
      - [x] 加载多个字典(-dmlmd,dict_mode_load_mult_dict)
    - [ ] 爆破模式(-bm,blast_mode)
      - [x] 目录长度范围(必选)
        - [x] 最小长度(-bmmin,blast_mode_min)
        - [x] 最大长度(-bmmax,blast_mode_max)
      - [ ] 基于默认字符集()
        - [ ] 基于a-z
        - [ ] 基于0-9
      - [x] 基于自定义字符集(-bmcc,blast_mode_custom_charset)
      - [x] 断点续生成payload(-bmrc,blast_mode_resume_charset)
    - [ ] 爬虫模式(-cm,Crawl Model)
      - [x] 自定义解析标签(-cmph,crawl_mode_parse_html)(a:href,img:src,form:action,script:src,iframe:src,div:src,frame:src,embed:src)
      - [ ] 解析robots.txt(-cmpr,crawl_mode_parse_robots)
      - [x] 爬虫类动态fuzz扫描(-cmdf,crawl_mode_dynamic_fuzz)
    - [x] fuzz模式(-fm,fuzz_mode)
      - [ ] fuzz单个字典(-fmlsd,fuzz_mode_load_single_dict)
      - [ ] fuzz多个字典(-fmlmd,fuzz_mode_load_mult_dict)
      - [x] fuzz标签(-fml,fuzz_mode_label)
  - [ ] 请求优化选项(RequestHandler)
    - [x] 自定义请求超时(-rt,request_timeout)
    - [x] 自定义请求延时(-rd,request_delay)
    - [x] 限制单个主机协程数扫描(-rl,request_limit)
    - [ ] 限制重试次数(-rmr,request_max_retries)
    - [ ] http持久连接(-rpc,request_persistent_connect)
    - [x] 自定义请求方法(-rm,request_method)(get、head)
    - [x] 302状态处理(-r3,redirection_302)(是否重定向)
    - [x] 自定义header
      - [x] 自定义其他header(-rh,request_headers)(解决需要401认证)
      - [x] 自定义ua(-rhua,request_header_ua)
      - [x] 自定义cookie(-rhc,request_header_cookie)
  - [ ] 字典处理选项(PayloadHandler)
    - [ ] 字典处理(payload修改-去斜杠)
    - [ ] 字典处理(payload修改-首字符加斜杠)
    - [ ] 字典处理(payload修改-单词首字母大写)
    - [ ] 字典处理(payload修改-去扩展)
    - [ ] 字典处理(payload修改-去除非字母数字)
  - [ ] 响应结果处理模块(ResponseHandler)
    - [x] 跳过大小为x字节的文件(-ss,skip_size)
    - [x] 自定义404页面(-c4p,custom_404_page)
    - [ ] 自定义503页面(-c5p,custom_503_page)
    - [ ] 自定义正则匹配响应内容并进行某种操作
      - [x] 自定义正则匹配响应(-crp,custom_response_page)
      - [ ] 某种操作(暂时未定义)
    - [x] 输出结果为自定义状态码(-rsc,response_status_code)
    - [x] 输出payload为完整路径
    - [x] 输出结果展示content-type
    - [x] 生成txt报告
  - [ ] 状态处理模块(StatusHandler)
    - [ ] 状态显示(等待开始、进行中、暂停中、异常、完成)
    - [x] 进度显示
    - [ ] 状态控制(开始、暂停、继续、停止)
    - [ ] 续扫模块(暂未配置)
    - [ ] 断点续扫
    - [ ] 选行续扫
  - [ ] 日志记录模块(ScanLogHandler)
    - [ ] 扫描日志
    - [ ] 错误日志
  - [ ] 代理模块(ProxyHandler)
    - [x] 单个代理(-ps,proxy_server)
    - [ ] 代理池
  - [x] 调试模式选项(DebugMode)
    - [x] debug(--debug)
  - [ ] 检查更新选项(CheckUpdate)
    - [ ] update(--update)

# 默认字典文件

1. dict_mode_dict.txt       字典模式字典，使用dirsearch默认字典
2. crawl_mode_suffix.txt    爬虫模式字典，使用FileSensor默认字典
3. fuzz_mode_dir.txt        fuzz模式字典，使用DirBuster默认字典
4. fuzz_mode_ext.txt        fuzz模式字典，使用常见后缀制作的字典
5. mult                     该目录可以存放多个用户自定义字典文件，用于批量字典加载

# 使用方法

## 环境准备

```
python3 -m pip install -r requirement.txt
```

## 快速使用


## 运行dirmap

### 单个目标

```shell
python3 dirmap.py -iU https://target.com -lcf
```

### 多个目标

```shell
python3 dirmap.py -iF urls.txt -lcf
```

## 高级使用(自定义dirmap配置)

暂时采用加载配置文件的方式进行详细配置，**不支持使用命令行参数进行详细配置**！

编辑根目录下的`dirmap.conf`，进行配置

`dirmap.conf`配置详解

```
#递归扫描处理配置
[RecursiveScan]
#是否开启递归扫描:关闭:0;开启:1
conf.recursive_scan = 0
#递归扫描深度。选项暂时不可用
conf.recursion_depth = 0
#设置排除扫描的目录
#conf.exclude_subdirs = ['/test1','/test2']
conf.exclude_subdirs = ""

#扫描模式处理配置(4个模式，1次只能选择1个)
[ScanModeHandler]
#字典模式:关闭:0;单字典:1;多字典:2
conf.dict_mode = 1
#单字典模式的路径
conf.dict_mode_load_single_dict = "\\dict_mode_dict.txt"
#多字典模式的路径，默认为:mult
conf.dict_mode_load_mult_dict = "\\mult\\"
#爆破模式:关闭:0;开启:1
conf.blast_mode = 0
#生成字典最小长度
conf.blast_mode_min = 1
#生成字典最大长度
conf.blast_mode_max = 3
#默认字符集:a-z
conf.blast_mode_az = "abcdefghijklmnopqrstuvwxyz"
#默认字符集:0-9
conf.blast_mode_num = "0123456789"
#自定义字符集
conf.blast_mode_custom_charset = "test"
#自定义继续字符集
conf.blast_mode_resume_charset = ""
#爬虫模式:关闭:0;开启:1
conf.crawl_mode = 0
#解析robots.txt文件
conf.crawl_mode_parse_robots = 0
#解析html页面的xpath表达式
conf.crawl_mode_parse_html = "//*/@href | //*/@src | //form/@action"
#是否进行动态爬虫字典生成:关闭:0;开启:1
conf.crawl_mode_dynamic_fuzz = 0
#Fuzz模式:关闭:0;单字典:1;多字典:2
conf.fuzz_mode = 0
#单字典模式的路径
conf.fuzz_mode_load_single_dict = "\\fuzz_mode_dir.txt"
#多字典模式的路径，默认为:mult
conf.fuzz_mode_load_mult_dict = "\\mult\\"
#设置fuzz标签e.g. {dir};{ext}
#conf.fuzz_mode_label = "{ext}"
conf.fuzz_mode_label = "{dir}"

#处理payload配置
[PayloadHandler]

#处理请求配置
[RequestHandler]
#自定义请求头。输入格式e.g:test1=test1,test2=test2
conf.request_headers = ""
#自定义请求User-Agent
conf.request_header_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
#自定义请求cookie。 e.g:cookie1=cookie1; cookie2=cookie2;
conf.request_header_cookie = ""
#自定义401认证。
conf.request_header_401_auth = ""
#自定义请求方法。默认get
conf.request_method = "get"
#自定义每个请求超时时间。默认2秒
conf.request_timeout = 2
#自定义每个请求，随机延迟(0-x)秒。参数必须是整数
conf.request_delay = 0
#自定义单个目标，请求协程线程数
conf.request_limit = 30
#自定义最大重试次数
conf.request_max_retries = 1
#设置持久连接。是否使用session()。未实现
conf.request_persistent_connect = 0
#这是302重定向e.g. True;False
conf.redirection_302 = False
#payload后添加后缀
conf.file_extension = ""

#处理响应配置
[ResponseHandler]
#设置要记录的响应状态。e.g. 200,403,301
conf.response_status_code = [200]
#是否记录content-type响应头
conf.response_header_content_type = 0
#自定义匹配404页面正则
conf.custom_404_page = "fake 404"
#自定义匹配503页面正则
conf.custom_503_page = "page 503"
#自定义正则表达式，匹配页面内容
conf.custom_response_page = "([0-9]){3}([a-z]){3}test"
#跳过显示页面大小为x的页面，若不设置，请配置成"None"，其他配置大小参考e.g:None;0b;1k;1m
conf.skip_size = "None"

#代理选线
[ProxyHandler]
conf.proxy = 1
#代理配置:e.g:{"http":"http://127.0.0.1:8080","https":"https://127.0.0.1:8080"}
#conf.proxy_server = {"http":"http://127.0.0.1:8080","https":"https://127.0.0.1:8080"}
conf.proxy_server = None

#Debug选项
[DebugMode]
#打印payloads并退出
conf.debug = 0

#update选项
[CheckUpdate]
#github获取更新。暂未实现。
conf.update = 0
```

# 维护工作

1. 若使用过程中出现问题，欢迎发issue
2. 本项目正在维护，未来将会有新的功能改进，具体参照“功能特点”列表，未打勾项
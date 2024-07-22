# -*- coding: utf-8 -*-
# @File    : helper.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:08
# @Explain : 助手类


import os
import sys
import random
import re
import hashlib
from urllib.parse import urlparse, parse_qs, urlencode
import json
import requests
import datetime

import socket
import uuid

from loguru import logger

logger_info = logger.info
logger_success = logger.success
logger_warning = logger.warning
logger_error = logger.error
logger_debug = logger.debug
logger_critical = logger.critical
logger_exception = logger.exception

def logger_(tag, value):
    if tag == 'info':
        logger.info(value)
    elif tag == 'success':
        logger.success(value)
    elif tag == 'warning':
        logger.warning(value)
    elif tag == 'error':
        logger.error(value)
    elif tag == 'debug':
        logger.debug(value)
    elif tag == 'critical':
        logger.critical(value)
    elif tag == 'exception':
        logger.exception(value)
    else:
        logger.info(value)

def get_obj_attr(obj, key):
    if hasattr(obj, key):
        val = getattr(obj, key)
    else:
        val = None
    return val

def remove_blank_lines(source_str):
    source_str = re.sub(r'\r\n', '\n', source_str)
    source_str = re.sub(r'\n\s*\n', '\n', source_str)
    return source_str

def get_dir(path):
    path = path.rstrip('/')
    dir = path[:path.rfind('/')]
    return dir

def get_current_name(filepath):
    current_file_name = os.path.basename(filepath)
    # current_file_path = os.path.abspath(filepath)
    # superior_file_path = os.path.dirname(filepath)
    current_name = os.path.splitext(current_file_name)[0]
    return current_name

def auto_make_dirs(path, is_dir=False):
    s_dir = path if is_dir else get_dir(path)
    if not os.path.exists(s_dir):
        os.makedirs(s_dir)
    return s_dir

def auto_make_file(filepath, clear=False):
    auto_make_dirs(filepath)
    if (not os.path.exists(filepath)) or clear is True:
        with open(filepath, mode='w', encoding='utf-8') as ff:
            ff.write('')

def content_to_lists(content, separator='\n'):
    data_list = []
    data_list = content.split(separator)
    data_list = [i for i in map(lambda v: v.strip(), data_list)]
    # data_list = list(filter(lambda v: v != '', data_list))
    data_list = [element for element in data_list if element != ""]
    return data_list

def content_to_map(content):
    data_list = content_to_lists(content, separator='\n')
    data_map = {}
    for element in data_list:
        element = element.split('=')
        key = element[0].strip().strip('\r\n')
        val = element[1].strip().strip('\r\n')
        data_map[key] = val
    return data_map

def map_to_content(map):
    data_list = []
    for k, v in map.items():
        data_list.append(f'{k}={v}')
    content = "\n".join(data_list)
    return content

def file_to_map(filepath):
    data_list = file_to_lists(filepath)
    data_list = [i for i in map(lambda v: get_pure_source(v.strip()), data_list)]
    data_list = [element for element in data_list if element != ""]
    data_map = {}
    for element in data_list:
        element = element.split('=')
        key = element[0].strip().strip('\r\n')
        val = element[1].strip().strip('\r\n') if len(element) > 1 else ''
        match = re.match(r'([\'"])(.+)\1', val)
        if match is not None:
            val = match.group(2)
        pass
        data_map[key] = val
    return data_map

def file_to_lists(filepath):
    data_list = []
    if os.path.exists(os.path.abspath(filepath)):
        try:
            with open(filepath) as f:
                data_list = f.readlines()
        except Exception as e:
            data_list = []
    data_list = [i for i in map(lambda v: v.strip(), data_list)]
    data_list = [element for element in data_list if element != ""]
    return data_list

def get_list_index(arr=None, item=''):
    # return [i for i in range(len(arr)) if arr[i] == item]
    return [index for (index, value) in enumerate(arr) if value == item]

# 获取文件内容代码
def get_file_source(filepath):
    source_str = ''
    if os.path.exists(os.path.abspath(filepath)):
        with open(os.path.abspath(filepath), 'r', encoding='utf-8') as f:
            source_str = f.read()
    return source_str

# 去除注释等 获取清纯代码
def get_pure_source(source_str):
    # 去除注释： 以#开头的行，并去除行首的空白字符
    pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
    source_str = pattern.sub('', source_str)
    pattern = re.compile(r'[ \f\t\v]*#.*$', re.MULTILINE)
    source_str = pattern.sub('', source_str)
    return source_str

def write_file_source(filepath, source_str):
    with open(os.path.abspath(filepath), 'w+', encoding='utf-8') as f:
        if os.path.isfile(filepath):
            f.truncate()
        else:
            pass
        # 去除空白行
        source_str = remove_blank_lines(source_str)
        f.write(source_str)

def write_map_to_file(filepath, map):
    source_str = remove_blank_lines()
    pass

def get_str_file_line_index(filepath, search_str=''):
    line_no = -1
    if os.path.exists(os.path.abspath(filepath)):
        try:
            with open(filepath) as f:
                line_no = [num for num, line in enumerate(f) if str(search_str) in line][0]
        except Exception as e:
            line_no = -1
    return line_no

def md5(val):
    m = hashlib.md5()
    m.update(str(val).encode(encoding='utf-8'))
    return m.hexdigest()

def sha1(val):
    m = hashlib.sha1()
    m.update(str(val).encode(encoding='utf-8'))
    return m.hexdigest()

def get_url_not_param(url):
    url = url[0:url.find('?')] if url.find('?') > 0 else url
    return url

def get_url_path(url):
    url = get_url_not_param(url)
    _url = urlparse(url)
    # hostname = _url.hostname
    # port = _url.port
    # url_port = _url.netloc
    # url_protocol = _url.scheme
    url_path = _url.path
    return url_path

def get_fix_uri(uri):
    param = parse_qs(urlparse(uri).query)
    # logger_info(f'param: {repr(param)}')
    param = dict(sorted(param.items()))  # 按键进行排序
    # logger_info(f'param: {repr(param)}')
    param = {key: param[key][0] for key in param}
    url_path = urlparse(uri).path
    url_scheme = urlparse(uri).scheme
    url_netloc = urlparse(uri).netloc
    # logger_info(f'url_path: {repr(url_path)}')
    # logger_info(f'url_scheme: {repr(url_scheme)}')
    # logger_info(f'url_netloc: {repr(url_netloc)}')
    url_param = urlencode(param)
    url_param = '?' + url_param if url_param is not None and url_param != '' else ''
    fix_uri = f'{url_scheme}://{url_netloc}{url_path}' + ('') + url_param
    # logger_info(f'fix_uri: {repr(fix_uri)}')
    return fix_uri

def tostr(s):
    return '' if s is None else str(s)

def dict_merge(dict1, dict2):
    merge_ = {**dict1, **dict2}
    return merge_

def get_dict_value(dict_, key, default=None):
    if key in dict_:
        value = dict_.get(key) if dict_.get(key) else default
    else:
        value = dict_.get(key, default)
    return value

def is_valid_uuid(string):
    try:
        # 将输入的字符串转换成UUID对象
        u = uuid.UUID(string)
        # 如果能正常转换并且不包含任何错误信息，则说明该字符串是有效的UUID
        return True
    except ValueError as e:
        # 若无法转换或者存在其他错误，返回False
        return False
    pass

def is_number(str):
  return str.isdigit()

# 判断字符串是否为带小数的数字
def is_decimal_number(str):
  try:
    float(str)
    return True
  except ValueError:
    return False
  pass

# 获取外网ip地址
def get_public_ip():
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="15", "Not.A/Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        # response = requests.request(url="https://api.ipify.org", method='GET', headers=dict_merge(headers, {'Referer': 'https://api.ipify.org'}), timeout=20)
        # response = request_url(url="https://api.ipify.org", method='GET', headers=dict_merge(headers, {'Referer': 'https://api.ipify.org'}), timeout=20, max_times=1)
        # response = requests.get("https://2023.ipchaxun.com/", headers=dict_merge(headers, {'Referer': 'https://2023.ipchaxun.com/'}), timeout=20)
        response = requests.get("https://www.ipplus360.com/getIP",
                                headers=dict_merge(headers, {'Referer': 'https://www.ipplus360.com/getIP'}), timeout=20)
        # response = requests.get("http://httpbin.org/ip", headers=dict_merge(headers, {'Referer': 'http://httpbin.org/ip'}), timeout=20)
        if response.status_code == 200:
            # ip = tostr(response.text)
            info = json.loads(str(response.text))
            # ip = tostr(info.get('ip', ''))
            ip = tostr(info.get('data', ''))
            # ip = tostr(info.get('origin', ''))
            return ip
        else:
            return None

    except Exception as e:
        logger_error(f"获取IP地址失败: {repr(e)}")
        return None

# 获取本机ip地址
def get_local_ip():
    ip_address = ''
    try:
        try:
            # 创建一个 UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 使用连接到本地回环地址的 socket 获取本地 IP 地址
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
        except Exception as e:
            # print("获取本地 IP 地址时出错：", e)
            ip_address = ''
        finally:
            s.close()
        pass
        if ip_address is None or ip_address == "" or ip_address == "127.0.0.1":
            ip_address = get_public_ip()  # 改用外网ip
        pass
    except:
        pass
    return ip_address

# 获取计算机名称
def get_hostname():
    hostname = socket.gethostname()
    return hostname

# 获取网卡地址
def get_mac_address():
    guid = uuid.getnode()
    mac = uuid.UUID(int=guid).hex[-12:]
    return mac

# 获取CPU序列号
def get_cpu_serial():
    cpu_serial = str(uuid.getnode())
    return cpu_serial

def get_user_agent():
    user_agent = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    ]
    return random.choice(user_agent)

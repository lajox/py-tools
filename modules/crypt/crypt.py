# -*- coding: utf-8 -*-
# @File    : psutil.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:08
# @Explain : psutil工具类


import hashlib
import base64
from loguru import logger

from common.helper.helper import *
from modules.common.common import *


def md5(val):
    m = hashlib.md5()
    m.update(str(val).encode(encoding='utf-8'))
    md5_hash = m.hexdigest()
    # md5_hash = hashlib.md5(str(val).encode()).hexdigest()
    return md5_hash


def sha1(val):
    m = hashlib.sha1()
    m.update(str(val).encode(encoding='utf-8'))
    sha1_hash = m.hexdigest()
    # sha1_hash = hashlib.sha1(str(val).encode()).hexdigest()
    return sha1_hash


def base64encode(val):
    base64_encode_str = base64.b64encode(str(val).encode('utf-8')).decode('utf-8')
    return base64_encode_str


def base64decode(val):
    base64_decode_str = base64.b64decode(str(val).encode('utf-8')).decode('utf-8')
    return base64_decode_str
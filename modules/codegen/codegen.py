# -*- coding: utf-8 -*-
# @File    : psutil.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:08
# @Explain : psutil工具类


import os
from loguru import logger
import subprocess
import pymysql
from pymysql import OperationalError

from common.helper.helper import *
from modules.common.common import *


def get_model_code(connection_str=''):
    # 设置 creationflags
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    output = ''
    try:
        connection_str = connection_str if connection_str else 'mysql+pymysql://root:hQwyGj7R@192.168.1.200/dscms_stock'
        exec_result = subprocess.run(['sqlacodegen', connection_str], capture_output=True, encoding='utf-8', creationflags=creationflags)
        output = exec_result.stdout.strip()
    except Exception as e:
        logger.error(e)
    pass
    return output


def check_soft_install(softname=''):
    try:
        # 尝试运行 `softname --version` 命令来获取 软件 版本
        result = subprocess.run([f'{softname}', '--version'], capture_output=True, text=True, check=True)
        soft_version = result.stdout.strip()
        logger.debug(f"{softname} 已安装，版本为: {soft_version}")
        return True, soft_version
    except subprocess.CalledProcessError:
        logger.debug(f"{softname} 未安装")
        return False, None
    except FileNotFoundError:
        logger.debug(f"{softname} 未安装")
        return False, None


def testing_mysql_connection(connection_string):
    # 解析连接字符串
    try:
        logger.debug(f"connect_string: {connection_string}")
        logger.debug("Testing MySQL connection...")
        # 解析连接字符串 mysql+pymysql://username:password@host/database
        # 解析连接字符串 mysql://username:password@ip:port/db?charset=utf8mb4
        connection_string = connection_string.replace('mysql+pymysql://', 'http://')
        connection_string = connection_string.replace('mysql://', 'http://')
        connection_string = connection_string if connection_string.startswith('http://') else 'http://' + connection_string

        url = urlparse(connection_string)
        # logger.debug(url)

        username = url.username
        password = url.password
        hostname = url.hostname
        port = url.port if url.port else 3306  # 默认 MySQL 端口是 3306
        database = url.path[1:].split('?')[0]  # 去掉路径开头的 '/'
        charset = url.query.split('=')[1] if 'charset=' in url.query else ''

        logger.debug((hostname, port, username, password, database))

        # 尝试连接数据库
        connection = pymysql.connect(
            host=hostname,
            user=username,
            password=password,
            database=database,
            port=port,
            charset=charset
        )

        logger.debug("Connection successful!")
        connection.close()
        return True
    except OperationalError as e:
        logger.error(f"Connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False
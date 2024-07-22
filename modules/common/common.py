# -*- coding: utf-8 -*-
# @File    : common.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 15:07
# @Explain : 公共模块


## 不用PySide2，改用PySide6，提升稳定性。但为了兼容win7 继续使用这段
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox, QShortcut, QWidget, QDialog, QPlainTextEdit, QPushButton
from PySide2.QtUiTools import QUiLoader, loadUiType
from PySide2.QtGui import QGuiApplication, QIcon, QKeySequence, QFont, QPixmap
from PySide2.QtCore import Qt, QTimer, QFileInfo, QDate, QDateTime
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QThread, QWaitCondition, QMutex, Qt, QObject, Signal

## 改用PySide6，提升稳定性 (win10系统以上运行的可以把上面那段注释掉切换为这段)：
# from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QDialog, QPlainTextEdit, QPushButton
# from PySide6.QtUiTools import QUiLoader, loadUiType
# from PySide6.QtGui import QGuiApplication, QIcon, QKeySequence, QFont, QAction, QShortcut, QTextCursor, QPixmap
# from PySide6.QtCore import Qt, QTimer, QFileInfo, QDate, QDateTime
# from PySide6.QtWidgets import QFileDialog
# from PySide6.QtCore import QThread, QWaitCondition, QMutex, Qt, QObject, Signal

from common.helper.helper import *
from common.thread.thread import Thread as Thread

import tkinter as tk
from tkinter import messagebox

import threading
import os
import sys
import platform
import time
import datetime
import json
from loguru import logger
import requests
from requests.adapters import HTTPAdapter

import uuid
# import socket

import atexit
import signal


# 请求地址，增加重试机制
def request_url(method, url, params=None, cookies=None, headers=None, json_data=None, timeout=20, max_times=0):
    max_times = int(max_times) if max_times is not None and max_times > 0 else 1
    timeout = int(timeout) if timeout is not None and timeout > 0 else 20

    # try_time = 0
    # while try_time < max_times:
    #     try:
    #         response = requests.request(method=method, url=url, params=params, cookies=cookies, headers=headers, json=json_data, timeout=timeout)
    #         break
    #     except Exception as e:
    #         logger.error(f'[request-except]: {repr(e)}')
    #         try_time += 1

    s = requests.session()
    # 设置重连次数
    s.mount('http://', HTTPAdapter(max_retries=max_times))
    s.mount('https://', HTTPAdapter(max_retries=max_times))
    # # s.verify = False
    # logger.debug(f'[request-url]: {repr(url)}')
    response = s.request(method=method, url=url, params=params, cookies=cookies, headers=headers, json=json_data, timeout=timeout)
    return response


def get_api_request(method='', url='', params={}, json_data={}, default_msg=''):
    status = 'false'
    data = None
    try:
        response = request_url(method=method, url=url, params=params, cookies={}, headers={}, json_data=json_data,
                               timeout=30, max_times=1)
        response_content = str(response.content.decode('utf-8'))
        logger.debug(response_content)
        response_status_code = response.status_code
        resp_data = json.loads(str(response_content))
        if resp_data.get('status', '') != '':
            status = resp_data.get('status', 'false')
            message = resp_data.get('message', default_msg)
        else:
            ret = resp_data.get('ret', -1)
            status = 'true' if ret == 0 else 'false'
            message = resp_data.get('msg', default_msg)
        if status == 'true':
            data = resp_data.get('data', None)
    except Exception as e:
        response_status_code = 500
        if isinstance(e, requests.exceptions.ProxyError):
            logger.error(f'[request-exception-ProxyError]: {repr(e)}')
        elif isinstance(e, requests.exceptions.ConnectionError):
            logger.error(f'[request-exception-ProxyError]: {repr(e)}')
        else:
            logger.error(f'[request-exception-Error]: {repr(e)}')
        # response.raise_for_status()
        response_status_code = response_status_code if response_status_code is not None and response_status_code != '' else 500
        status = 'false'
        message = str(repr(e))
    finally:
        pass

    ret = {'status': status, 'message': message, 'data': data}
    return ret


def message_box(content='内容', title='提示', type='information'):
    """
    :param content: 内容
    :param title: 标题
    :param type: 类型，值有 information, about, warning, critical
    :return:
    """
    type = type if type is not None and type != '' else 'information'
    MainWindow = QMainWindow()
    MessageBox = QMessageBox()
    if type == 'information':
        MessageBox.information(MainWindow, title, content)
    elif type == 'about':
        MessageBox.about(MainWindow, title, content)
    elif type == 'warning':
        MessageBox.warning(MainWindow, title, content)
    elif type == 'critical':
        MessageBox.warning(MainWindow, title, content)
    else:
        MessageBox.information(MainWindow, title, content)


def question_box(content='内容', title='提示'):
    MainWindow = QMainWindow()
    MessageBox = QMessageBox()
    Ret = MessageBox.question(MainWindow, title, content)
    return Ret


def show_tk_box(message='', title='提示'):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo(title=title, message=message)
    root.mainloop()


# 弹窗提示（Tk）
def show_tk_alert(message='', title='提示'):
    # 实例化object，建立窗口window
    window = tk.Tk()

    # 给窗口的可视化起名字
    window.title(title)
    # 设置正中央位置
    screenWidth = window.winfo_screenwidth()  # 获取显示区域的宽度
    screenHeight = window.winfo_screenheight()  # 获取显示区域的高度
    width = 300  # 设定窗口宽度
    height = 160  # 设定窗口高度
    left = (screenWidth - width) / 2
    top = (screenHeight - height) / 2

    # 宽度x高度+x偏移+y偏移
    # 在设定宽度和高度的基础上指定窗口相对于屏幕左上角的偏移位置
    window.geometry("%dx%d+%d+%d" % (width, height, left, top))
    # 设置窗口置顶
    window.wm_attributes('-topmost', 1)
    # 禁用最大化按钮
    window.resizable(height=False, width=False)

    # 在图形界面上设定标签
    l = tk.Label(window, text=message, font=(96), width=30, height=30)
    # 说明： bg为背景，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高

    # 放置标签
    l.pack()  # Label内容content区域放置位置，自动调节尺寸 （ 放置lable的方法有：1 l.pack(); 2 l.place();）

    # 主窗口循环显示
    window.mainloop()


def show_message_box(message='', title=''):
    # message_box(message, title)  # 使用 MessageBox 在线程中会崩溃
    # t = threading.Timer(1, lambda: message_box(message, title))
    # t.start()
    # show_tk_alert(message=message, title=title)
    show_tk_box(message=message, title=title)


def get_client_ip():
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(('8.8.8.8', 80))
    # ip = s.getsockname()[0]
    # s.close()
    ip = get_public_ip()
    ip = tostr(ip)
    return ip


# 获取客户端信息
def get_client_info():
    # 获取CPU序列号
    cpu_serial = get_cpu_serial()
    # 获取网卡地址
    mac_address = get_mac_address()

    client_info = f"{cpu_serial}@{mac_address}"
    return client_info


def is_windows():
    return sys.platform.startswith('win')

def is_linux():
    return sys.platform.startswith('linux')

def is_macOS():
    return sys.platform.startswith('darwin')


# TaskThread = threading.Thread
class TaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super(TaskThread, self).__init__(*args, **kwargs)
        pass

    def task(self):
        pass


class ThreadWork(QThread):
    updated = Signal(str)  # 修改为接收字符串类型的参数

    def __init__(self):
        super().__init__()
        self.text = ''

    def setText(self, text):
        self.text = text

    def run(self):  # 增加参数
        # 在子线程中进行一些操作
        self.updated.emit(self.text)


class ThreadTodo(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ThreadTodo, self).__init__(*args, **kwargs)
        self.timeout = 0
        self.fn = None

    def setTimeout(self, timeout):
        self.timeout = timeout

    def run(self):  # 增加参数
        # 在子线程中进行一些操作
        if self.timeout and self.timeout > 0:
            time.sleep(self.timeout)
        pass
        if self._target is not None:
            self._target(*self._args)
        pass
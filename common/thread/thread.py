# -*- coding: utf-8 -*-
# @File    : thread.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:22
# @Explain : 线程操作类


import threading


class Thread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()         # 用于暂停线程的标识
        self.__flag.set()                       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()                    # 将running设置为True

    def run(self):
        # print('---run---')
        while self.is_running():
            self.__flag.wait()        # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            if self._target is not None:
                self._target(*self._args)
            else:
                self.task()
            pass
        pass

    def task(self):
        pass

    def pause(self):
        self.__flag.clear()           # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()             # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()             # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()        # 设置为False

    def wait(self):
        pass

    def is_running(self):
        return self.__running.isSet()

    def is_paused(self):
        return not self.__flag.isSet()
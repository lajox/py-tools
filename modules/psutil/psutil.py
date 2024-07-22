# -*- coding: utf-8 -*-
# @File    : psutil.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:08
# @Explain : psutil工具类


import psutil

from common.helper.helper import *
from modules.common.common import *


def pid_exists(process_pid):
    return psutil.pid_exists(int(process_pid))


def port_exists(port):
    is_exists = False
    if is_windows():
        res = []
        with os.popen(f'netstat -ano | findstr ":{port} "') as res:
            res = [i for i in re.split('\n', res.read()) if i != '']
        result = []
        for line in res:
            temp = [i for i in re.split('[\s]+', line.strip()) if i != '']
            if len(temp) > 4:
                result.append({'pid': temp[4], 'address': temp[1], 'state': temp[3]})
            pass
        if len(result) > 0:
            pids = []
            for row in result:
                if row['address'].split(':')[-1] == str(port):
                    pids.append(row['pid'])
                pass
            pass
            if len(pids) > 0:
                is_exists = True
            pass
        pass
    else:
        # cmd = 'netstat -lntp | grep ":6379 "'
        res = []
        with os.popen('lsof -i:' + str(port)) as res:
            res = [i for i in re.split('\n', res.read()) if i != '']
        result = []
        for line in res:
            temp = [i for i in re.split('[\s]+', line.strip()) if i != '']
            if len(temp) > 4:
                # COMMAND  PID  USER  FD  TYPE  DEVICE  SIZE/OFF  NODE  NAME
                result.append({'pid': temp[1], 'comand': temp[0], 'user': temp[2], 'name': temp[8]})
            pass
        if len(result) > 0:
            is_exists = True
        pass
    return is_exists


# 根据pid获取进程信息
def find_pid_info(pid):
    pid_info = None
    if is_windows():
        cmd = f'tasklist /NH /FI "pid eq {pid}"'
        # 映像名称   PID   会话名   会话#   内存使用
        message = os.popen(f"{cmd}")
        console = message.read().strip()
        message.close()
        if console != "" and console.find(f"{pid}") >= 0:
            res_a = [i for i in re.split('[\s]+', console) if i != '']
            imagename = res_a[0]
            cmd = f"wmic process get commandline,executablepath,name,processid /format:csv | findstr {pid} | findstr /v findstr | findstr {imagename}"
            logger.debug(cmd)
            message = os.popen(f"{cmd}")
            console = message.read().strip()
            # logger.debug(console)
            message.close()
            if console != "" and console.find(f"{imagename}") >= 0 and console.find(f"{pid}") >= 0:
                temp = [i.strip() for i in re.split(',', console) if i.strip() != '']
                # logger.debug(temp)
                pid_info = {"commandline": temp[0], "executablepath": temp[1], "name": temp[2], "processid": temp[3]}
            pass
        pass
    else:
        cmd = f'ps -p {pid} -o comm,user,group,pid,ppid,cputime,etimes,cmd --no-headers'
        # COMMAND  USER  GROUP  PID  PPID  TIME  ELAPSED  CMD
        message = os.popen(f"{cmd}")
        console = message.read().strip()
        message.close()
        if console != "" and console.find(f"{pid}") >= 0:
            temp = [i for i in re.split('[\s]+', console) if i != '']
            str_cmd = temp[7]
            if len(temp) > 8:
                arr_cmd = []
                for i in range(7, len(temp)):
                    arr_cmd.append(temp[i])
                pass
                str_cmd = " ".join(arr_cmd)
            pass
            pid_info = {'command': temp[1], 'user': temp[1], 'group': temp[2], 'pid': temp[3], 'ppid': temp[4], 'cmd': str_cmd}
        pass
    pass
    return pid_info


def find_pids(port=None, name=None):
    pids = []
    if port:
        if is_windows():
            with os.popen(f'netstat -ano | findstr ":{port} "') as res:
                res = [i for i in re.split('\n', res.read()) if i != '']
            result = []
            for line in res:
                temp = [i for i in re.split('[\s]+', line.strip()) if i != '']
                if len(temp) > 4:
                    result.append({'pid': temp[4], 'address': temp[1], 'state': temp[3]})
                pass
            pass
            for row in result:
                if row['address'].split(':')[-1] == str(port):
                    pids.append(row['pid'])
                pass
            pass
        else:
            with os.popen('lsof -i:' + str(port)) as res:
                res = [i for i in re.split('\n', res.read()) if i != '']
            result = []
            for line in res:
                temp = [i for i in re.split('[\s]+', line.strip()) if i != '']
                if len(temp) > 4:
                    result.append({'pid': temp[1], 'command': temp[0], 'user': temp[2], 'name': temp[8]})
                pass
            for row in result:
                pids.append(row['pid'])
            pass
    elif name:
        if str(name).isdigit():
            if pid_exists(name):
                pids.append(str(name))
            pass
        else:
            # cmd = f'tasklist /FO TABLE /NH | findstr "{name}"'
            # message = os.popen(f"{cmd}")
            # console = message.read().strip()
            # message.close()
            # if console != "" and console.find(name) >= 0:
            #     logger.debug(console)
            #     lines = [v for v in console.split("\n") if v.strip() != '']
            #     logger.debug(lines)
            #     for line in lines:
            #         logger.debug(line)
            #         res = re.split(r"\s+", line, line.strip())
            #         pid = res[1]
            #         pids.append(pid)
            #     pass
            # pass

            name = name.replace('/', '\\').replace('\\', '\\\\')
            cmd = f'wmic process get commandline,processid /format:csv | findstr "{name}" | findstr /v findstr'
            logger.debug(f"{cmd}")
            message = os.popen(f"{cmd}")
            console = message.read().strip()
            message.close()
            if console != "" and console.find(name.replace('\\\\', '\\')) >= 0:
                lines = [v for v in console.split("\n") if v.strip() != '']
                for line in lines:
                    res = re.split(r",", line.strip())
                    pid = res[-1]
                    pids.append(pid)
                pass
            pass
    pass

    pids = list(set(pids))
    return pids


def kill_pid(pid):
    try:
        if is_windows():
            res = os.popen(f"taskkill /f /pid {pid}")
        else:
            # os.kill(pid, signal.SIGKILL)
            # os.kill(pid, signal.SIGTERM)
            res = os.popen("kill -9 " + str(pid))
        pass
        result = (not pid_exists(pid))
    except:
        result = False
    pass
    return result


def kill_name(name):
    # if is_windows():
    #     os.system(f"taskkill /f /im /t {name}")
    # pass
    try:
        pids = find_pids(name=name)
        for pid in pids:
            res = kill_pid(pid)
        pass
    except Exception as e:
        logger.error(str(e))
    pass


def kill_port(port):
    try:
        pids = find_pids(port=port)
        for pid in pids:
            res = kill_pid(pid)
        pass
    except Exception as e:
        logger.error(str(e))
    pass


# 结束和删除计划任务
def del_task(task):
    try:
        if task_exists(task):
            cmd = f'schtasks /end /tn "{task}"'
            os.system(cmd)
            cmd = f'schtasks /delete /tn "{task}"'
            os.system(cmd)
        pass
    except Exception as e:
        logger.error(str(e))
    pass


def task_exists(task):
    cmd = f'schtasks /query /tn "{task}"'
    try:
        message = os.popen(f"{cmd}")
        console = message.read().strip()
        message.close()
        if console != "" and console.find(task) >= 0:
            logger.debug(console)
            return True
        pass
    except:
        pass
    pass
    return False


def get_process_list():
    process_list = list(psutil.process_iter())
    for process in process_list:
        pid = process.pid
        name = process.name()
        status = process.status()
        logger.debug(f"进程ID: {pid}, 进程名: {name}, 进程状态: {status}")
    pass













class PsutilUtil:
    @staticmethod
    def get_cpu_percent():
        """
        获取CPU使用率
        :return: CPU使用率
        """

        return psutil.cpu_percent()
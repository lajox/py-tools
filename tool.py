# -*- coding: utf-8 -*-
# @File    : tool.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:26
# @Explain :


import sys
sys.path.append('..')

from version import *
from environ import *
from common.helper.helper import *
from modules.common.common import *
from modules.psutil.psutil import *
from modules.crypt.crypt import *
from modules.codegen.codegen import *

# -----------------------------------------------------------------------------------------

environ = APP_ENVIRON

if environ == 'production':
    logger.remove(handler_id=None)  # 清除之前的设置
    # 设置生成日志文件，utf-8编码，每天0点切割，zip压缩，保留3天，异步写入
    logger.add(sink='tool.log', level='INFO', rotation='00:00', retention='3 days', compression='zip', encoding='utf-8', enqueue=True)
    # logger.add(sink='tool.log', level='DEBUG', rotation='00:00', retention='3 days', compression='zip', encoding='utf-8', enqueue=True)
pass

# -----------------------------------------------------------------------------------------

global_root_path = os.path.dirname(os.path.realpath(sys.argv[0])).replace('\\', '/')

ui_loader = QUiLoader()

# -----------------------------------------------------------------------------------------


class Stats:

    def __init__(self):
        self.task = None
        self.ui = ui_loader.load('ui-templates/tool.ui')
        # 设置窗口图标
        self.ui.setWindowIcon(main_icon)
        self.ui.button_1.clicked.connect(lambda: self.process_todo('check_process'))  # 检测进程
        self.ui.button_2.clicked.connect(lambda: self.process_todo('kill_process'))  # 结束进程
        self.ui.button_3.clicked.connect(self.clearValue)
        self.ui.radioButton_1.clicked.connect(lambda: self.changeType(0))  # 端口
        self.ui.radioButton_2.clicked.connect(lambda: self.changeType(1))  # 进程
        self.ui.radioButton_3.clicked.connect(lambda: self.changeType(2))  # 计划任务
        self.ui.button_md5.clicked.connect(lambda: self.calculate_md5())
        self.ui.button_sha1.clicked.connect(lambda: self.calculate_sha1())
        self.ui.button_base64_1.clicked.connect(lambda: self.calculate_base64_encode())
        self.ui.button_base64_2.clicked.connect(lambda: self.calculate_base64_decode())
        self.ui.button_gen_model.clicked.connect(lambda: self.generate_model_code())
        self._last_directory = ""

        # 使用信号和槽机制，线程之间安全地通信
        self.thread = ThreadWork()
        self.thread.updated.connect(self.print)

    def safe_print(self, text):
        self.thread.setText(text)
        self.thread.start()  # 启动线程

    def init_show(self):
        self.ui.show()
        self.ui.radioButton_1.setChecked(True)
        self.ui.button_1.setText('检测端口')
        self.ui.button_2.setText('关闭端口')
        self.ui.lineEdit_1.setText('')
        self.clear()

    def changeType(self, type):
        if type == 0:
            self.ui.button_1.setText('检测端口')
            self.ui.button_2.setText('关闭端口')
        elif type == 1:
            self.ui.button_1.setText('检测进程')
            self.ui.button_2.setText('结束进程')
        elif type == 2:
            self.ui.button_1.setText('检测计划任务')
            self.ui.button_2.setText('删除计划任务')
        pass

    def process_todo(self, job):
        self.clear()
        type = 0
        if self.ui.radioButton_1.isChecked():  # 端口
            type = 0
        if self.ui.radioButton_2.isChecked():  # 进程
            type = 1
        if self.ui.radioButton_3.isChecked():  # 计划任务
            type = 2
        checkValue = self.ui.lineEdit_1.text().strip()
        if checkValue == '':
            # self.print('请输入内容值')
            message_box('请输入内容值')
            return
        if type == 0 and checkValue != '' and not checkValue.isdigit():
            # self.print('端口必须是整数数字')
            message_box('端口必须是整数数字')
            return
        if type == 0 and checkValue != '' and checkValue.isdigit() and (int(checkValue) < 0 or int(checkValue) > 65535):
            # self.print('端口范围必须是0到65535之间')
            message_box('端口范围必须是0到65535之间')
            return
        arg = (job, type, checkValue,)
        # self.task = threading.Thread(target=run_check_process, args=tuple(arg), name=f'run-check-process')
        self.task = TaskThread(target=run_check_process, args=tuple(arg), name=f'run-check-process')
        self.task.daemon = 1
        self.task.start()

    def calculate_md5(self):
        text = self.ui.lineEdit_origin.text()
        md5_hash = md5(text)
        self.ui.lineEdit_md5.setText(md5_hash)

    def calculate_sha1(self):
        text = self.ui.lineEdit_origin.text()
        sha1_hash = sha1(text)
        self.ui.lineEdit_sha1.setText(sha1_hash)

    def calculate_base64_encode(self):
        text = self.ui.plainTextEdit_base64_1.toPlainText()
        try:
            cal_str = base64encode(text)
            self.ui.plainTextEdit_base64_2.setPlainText(cal_str)
        except Exception as e:
            logger.error(e)
            self.ui.plainTextEdit_base64_1.setPlainText('')
        pass

    def calculate_base64_decode(self):
        text = self.ui.plainTextEdit_base64_2.toPlainText()
        try:
            cal_str = base64decode(text)
            self.ui.plainTextEdit_base64_1.setPlainText(cal_str)
        except Exception as e:
            logger.error(e)
            self.ui.plainTextEdit_base64_1.setPlainText('')
        pass

    def generate_model_code(self):
        text = self.ui.lineEdit_connect.text()
        try:
            # 检测软件是否安装
            softname = 'sqlacodegen'
            if not check_soft_install(softname):
                message_box(f'{softname} 未安装，请先安装\n\n请先执行 pip install {softname} 进行安装')
                return
            pass
            # 检测数据库是否连接
            if not testing_mysql_connection(text):
                message_box(f'数据库连接失败，请检查连接信息')
                return
            pass
            gen_code = get_model_code(text)
            self.ui.plainTextEdit_model_code.setPlainText(gen_code)
        except Exception as e:
            logger.error(e)
            self.ui.plainTextEdit_model_code.setPlainText('')
        pass

    def clearValue(self):
        self.ui.lineEdit_1.setText('')

    def print(self, text):
        self.ui.textBrowser.append(text)
        self.ui.textBrowser.moveCursor(self.ui.textBrowser.textCursor().End
                                       if hasattr(self.ui.textBrowser.textCursor(), 'End')
                                       else self.ui.textBrowser.textCursor().MoveOperation.End)

    def clear(self):
        self.ui.textBrowser.setText('')


def run_check_process(job='', type='', checkValue=''):
    app.ui.button_1.setDisabled(True)
    app.ui.button_2.setDisabled(True)

    time.sleep(0.5)

    app.safe_print(f'<font color="#000000">正在检测中,请稍等...</font>')
    logger.info('正在检测中,请稍等...')
    time.sleep(0.2)

    while True:
        ret = check_process_status(job=job, type=type, checkValue=checkValue)
        time.sleep(0.8)
        break
    pass

    app.safe_print(f'<font color="#000000">执行结束</font>')
    logger.info('执行结束')
    if app.task is not None and isinstance(app.task, TaskThread) and hasattr(app.task, 'stop'):
        app.task.stop()
    pass
    time.sleep(0.5)

    app.ui.button_1.setDisabled(False)
    app.ui.button_2.setDisabled(False)


def check_process_status(job='', type='', checkValue=''):
    type = int(type) if type else 0

    strTypes = ['端口', '进程', '计划任务']
    strDelTypes = ['关闭', '结束', '删除']

    app.safe_print(f'<font color="#000000">当前检测的{strTypes[type]}：{checkValue}</font>')
    logger.info(f'当前检测的{strTypes[type]}：{checkValue}')
    time.sleep(0.1)

    app.safe_print(f'<font color="#000000">正在检测{strTypes[type]}：{checkValue}</font>')
    logger.info(f'正在检测{strTypes[type]}：{checkValue}')

    result = ''
    process_pid = None
    checkStatus = False
    pids = []
    if job == 'check_process' or job == 'kill_process':
        # 检测端口或进程名
        if type == 0 or type == 1:
            if type == 0:
                pids = find_pids(port=checkValue)
            elif type == 1:
                pids = find_pids(name=checkValue)
            if pids and len(pids) > 0:
                checkStatus = True
                app.safe_print(f'<font color="#2C9E4B">已找到{strTypes[type]}：{checkValue}</font>')
                logger.info(f'已找到{strTypes[type]}：{checkValue}')
                time.sleep(0.1)
                for i, pid in enumerate(pids):
                    app.safe_print(f'<font color="#2C9E4B">第{i + 1}个进程ID: {pid}</font>')
                    logger.info(f'第{i + 1}个进程ID: {pid}')
                    pid_info = find_pid_info(pid)
                    if pid_info is not None:
                        if is_windows():
                            logger.info(f'进程信息：')
                            app.safe_print(f'<font color="#25618D">进程信息：</font>')
                            time.sleep(0.1)
                            logger.info(f'{pid_info.get("executablepath")}')
                            app.safe_print(f'<font color="#25618D">{pid_info.get("executablepath")}</font>')
                            time.sleep(0.1)
                        else:
                            logger.info(f'进程信息：')
                            app.safe_print(f'<font color="#25618D">进程信息：</font>')
                            logger.info(f'{pid_info.get("cmd")}')
                            time.sleep(0.1)
                            app.safe_print(f'<font color="#25618D">{pid_info.get("cmd")}</font>')
                            time.sleep(0.1)
                        pass
                    time.sleep(0.1)
                pass
            else:
                checkStatus = False
                app.safe_print(f'<font color="#FF0000">检测失败,未找到{strTypes[type]}：{checkValue}</font>')
                logger.info(f'检测失败,未找到{strTypes[type]}：{checkValue}')
                time.sleep(0.1)
            pass
        # 检测计划任务
        elif type == 2:
            checkStatus = task_exists(checkValue)
            if checkStatus:
                app.safe_print(f'<font color="#2C9E4B">{strTypes[type]}：{checkValue} 存在</font>')
                logger.info(f'{strTypes[type]}：{checkValue} 存在')
                time.sleep(0.1)
            else:
                app.safe_print(f'<font color="#FF0000">检测失败,未找到{strTypes[type]}：{checkValue}</font>')
                logger.info(f'检测失败,未找到{strTypes[type]}：{checkValue}')
                time.sleep(0.1)
            pass
    pass
    if job == 'kill_process':
        if checkStatus:
            app.safe_print(f'<font color="#000000">正在{strDelTypes[type]}{strTypes[type]}：{checkValue}</font>')
            logger.info(f'正在{strDelTypes[type]}{strTypes[type]}：{checkValue}')
            time.sleep(0.1)

            # 关闭端口或进程名
            if type == 0 or type == 1:
                if pids and len(pids) > 0:
                    for i, pid in enumerate(pids):
                        r = kill_pid(pid)
                        time.sleep(1)
                        if not pid_exists(pid):
                            app.safe_print(f'<font color="#2C9E4B">已结束第{i + 1}个进程ID：{pid}</font>')
                            logger.info(f'已结束第{i + 1}个进程ID：{pid}')
                            time.sleep(0.1)
                        else:
                            app.safe_print(f'<font color="#FF0000">结束第{i + 1}个进程ID：{pid} 关闭失败</font>')
                            logger.info(f'结束第{i + 1}个进程ID：{pid} 关闭失败')
                            time.sleep(0.1)
                        pass
                    pass
                pass
            # 删除计划任务
            elif type == 2:
                del_task(checkValue)
                time.sleep(1)
                if not task_exists(checkValue):
                    app.safe_print(f'<font color="#2C9E4B">{strTypes[type]}：{checkValue} 删除成功</font>')
                    logger.info(f'{strTypes[type]}：{checkValue} 删除成功')
                    time.sleep(0.1)
                else:
                    app.safe_print(f'<font color="#FF0000">{strTypes[type]}：{checkValue} 删除失败</font>')
                    logger.info(f'{strTypes[type]}：{checkValue} 删除失败')
                    time.sleep(0.1)
                pass
        pass
    pass
    time.sleep(0.5)

    return result

# 退出时的一些清理工作
def _clean_handler(port='', msecs=''):
    logger.debug('----clean_handler----')
    try:
        logger.debug('----cleaning begin----')
        pass
    except:
        pass
    finally:
        logger.debug('----cleaning end----')
        pass
    logger.debug('----clean_done----')
    logger.info('---- 软件正常关闭 ----')
    pass


def auto_clean():
    # 拦截的信号通过注册SIGINT（Ctrl+C）信号处理函数 来在用户按下Ctrl+C时执行清理操作
    signal.signal(signal.SIGTERM, _clean_handler)  # SIGTERM 关闭程序信号
    signal.signal(signal.SIGINT, _clean_handler)  # 接收ctrl+c 信号
    # 程序退出时要执行的清理操作
    atexit.register(_clean_handler)
    pass


if __name__ == '__main__':
    global_client_info = get_client_info()  # 获取客户端信息
    global_hostname = get_hostname()  # 获取计算机名称
    global_local_ip = get_local_ip()  # 获取本机ip地址
    global_client_ip = get_client_ip()  # 获取客户端ip
    auto_clean()
    logger.info(f'当前版本：{APP_VERSION}')
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    font = QFont("Arial")
    pointsize = font.pointSize()
    # font.setPixelSize(pointsize * 90 / 72)
    font.setPixelSize(12)
    font.setFamily("Arial")
    QApplication.setFont(font)
    ui = QApplication([])
    # 设置窗口图标
    main_icon = QIcon('build.ico')
    ico_path = os.path.join(global_root_path, 'build.ico')
    main_icon.addPixmap(QPixmap(ico_path), QIcon.Normal, QIcon.Off)
    app = Stats()
    #app.ui.show()
    app.init_show()
    app.ui.textBrowser.setFont(font)
    sys.exit(ui.exec() if hasattr(ui, 'exec') else ui.exec_())

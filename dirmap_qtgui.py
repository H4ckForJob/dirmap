import sys
import os

from gevent import monkey
monkey.patch_all()
from PyQt5.QtWidgets import QMainWindow,QGridLayout,QLabel,QLineEdit,QPushButton,QTableWidget,QWidget,QDesktopWidget,QApplication,QTableWidgetItem
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtCore import QThread,Qt,pyqtSignal
from gevent import monkey
monkey.patch_all()
from lib.controller.engine import run
from lib.core.common import setPaths
from lib.core.data import cmdLineOptions, conf, paths, tasks
from lib.core.option import initOptions
# from QCandyUi.CandyWindow import colorful
from QCandyUi import CandyWindow
# from lib.parse.cmdline import cmdLineParser

class WorkThread(QThread):
    stop = pyqtSignal()
    update = pyqtSignal(str,str,str,str)
    update_status =  pyqtSignal()

    def __int__(self):
        super(WorkThread, self).__init__()

    def run(self):
        run()
        self.stop.emit()  # 循环完毕后发出信号

# @colorful('blueGreen')
class DirmapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_stop = True
        self.initUI()

    def initUI(self):
        self.resize(1000, 600)
        self.center()
        self.setWindowTitle('Dirmap - PyQT')
        self.setWindowIcon(QIcon('dirmap.ico'))

        grid = QGridLayout()
        # grid.setSpacing(10)
        urlLable = QLabel('URL')
        urlLable.setAlignment((Qt.AlignRight | Qt.AlignVCenter))
        self.urlText = QLineEdit()
        startButton = QPushButton("开始")
        stopButton = QPushButton("结束")
        startButton.clicked.connect(self.start_button_clicked)
        stopButton.clicked.connect(self.stop_button_clicked)
        self.status = self.statusBar()
        self.status.showMessage("准备就绪,相关参数请自行修改配置文件,无需重启")

        grid.addWidget(urlLable, 0, 0)
        grid.addWidget(self.urlText, 0, 1, 1, 12)
        grid.addWidget(startButton, 0, 13)
        grid.addWidget(stopButton, 0, 14)

        self.tableWidget = QTableWidget()  # 创建一个表格
        # self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['地址', '类型', '大小', '响应码'])

        self.tableWidget.setColumnWidth(0, 570)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.horizontalHeader().setFixedHeight(30)
        grid.addWidget(self.tableWidget, 2, 0, 1, 15)  # 把表格加入布局

        wid_get = QWidget()
        wid_get.setLayout(grid)
        self.setCentralWidget(wid_get)

        # self.setLayout(grid)
        # self.show()

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_button_clicked(self):
        if not conf.is_stop:
            return
        text = self.urlText.text()
        if text == "": return
        conf.is_stop = False
        row_index = self.tableWidget.rowCount()
        for i in range(row_index):
            self.tableWidget.removeRow(0)

        paths.ROOT_PATH = os.getcwd()
        setPaths()
        dicts = {'thread_num': 8, 'target_input': text, 'target_file': '', 'load_config_file': True,
                 'debug': False}
        cmdLineOptions.update(dicts)
        initOptions(cmdLineOptions)
        # run()
        # self.stop_button_clicked()
        self.workThread = WorkThread()
        conf["thread"] = self.workThread
        self.workThread.start()
        self.workThread.stop.connect(self.stop_button_clicked)
        self.workThread.update.connect(self.update_table)
        self.workThread.update_status.connect(self.update_status_bar)

    def stop_button_clicked(self):
        conf.is_stop = True
        self.status.showMessage("扫描结束")
        tasks['task_count'] = 0
        while not tasks.all_task.empty():
            tasks.all_task.get(block=True, timeout=3)

    def update_table(self, url, types, size, code):
        print(url, types, size, code)
        row_index = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row_index + 1)
        url_item = QLabel()
        url_item.setOpenExternalLinks(True)
        url_item.setText(f"<a href='{url}'>{url}</a>")
        self.tableWidget.setCellWidget(row_index, 0, url_item)
        new_item = QTableWidgetItem(types)
        new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.tableWidget.setItem(row_index, 1, new_item)
        new_item = QTableWidgetItem(size)
        new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.tableWidget.setItem(row_index, 2, new_item)
        new_item = QTableWidgetItem(code)
        new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if code[0] == '2':
            new_item.setForeground(QColor("green"))
        elif code[0] == '3':
            new_item.setForeground(QColor("blue"))
        elif code[0] == '4':
            new_item.setForeground(QColor("red"))
        self.tableWidget.setItem(row_index, 3, new_item)

    def update_status_bar(self):
        if tasks['task_length']:
            message = f"{tasks['task_count']}/{tasks['task_length']}"
        else:
            message = str(tasks['task_count'])
        self.status.showMessage(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    conf["is_stop"] = True
    conf["ex"] = DirmapGUI()
    conf["ex"] = CandyWindow.createWindow(conf["ex"], 'blueGreen', title="DirMap - PyQT", ico_path="dirmap.ico")
    conf["ex"].show()
    app.setWindowIcon(QIcon('dirmap.ico'))
    sys.exit(app.exec_())
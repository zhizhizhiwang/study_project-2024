import logging
import math
import sys
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import numpy
from PyQt6 import QtCore, QtWidgets

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

set_dir: dict[str, int | None | list[int | float]] = defaultdict(lambda: None)
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None):

        fig, self.ax = plt.subplots()
        super().__init__(fig)

        self.x = numpy.arange(0, 10, 1)
        self.y = 2 * self.x + 1
        self.ax.scatter(self.x, self.y, label='2x + 1')
        self.ax.set_title('Matplotlib in PyQt6')
        self.ax.set_xlabel('n')
        self.ax.set_ylabel('a[n]')
        self.ax.legend()

        # 鼠标覆盖添加文本框
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                      textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="w"),
                                      arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        # 连接鼠标移动事件
        self.mpl_connect("motion_notify_event", self.hover)

    def set_y(self, command: str):
        logger.debug("set_y")
        seq_type = set_dir['mode']
        n = max(int(set_dir['max_index']), 10)
        expr = command.strip()
        if seq_type == 1:
            # 处理递推式

            initial = set_dir['init_number']

            a = initial.copy()
            current_length = len(initial)

            if n <= current_length:
                return numpy.array(a[:n])

            for k in range(current_length, n):
                context = {
                    'a': a,
                    'n': k,
                    'math': math
                }
                try:
                    current = eval(expr, context, math.__dict__)
                    a.append(current)
                except IndexError as e:
                    logger.error(f"初始项设置错误 : {e}")
                except Exception as e:
                    logger.error(f"计算递推式时出错：{e}")

        elif seq_type == 2:
            # 处理通项公式
            a = []
            for k in range(n):
                context = {
                    'n': k,
                    'math': math
                }
                try:
                    current = eval(expr, context, math.__dict__)
                    a.append(current)
                except Exception as e:
                    logger.error(f"计算通项时出错：{e}")


        else:
            logger.error("类型错误")
            return None

        self.y = numpy.array(a)
        logger.debug("set_y done")

    def update_image(self, command : str):
        logger.debug("update_image")
        self.set_y(command)
        n = max(int(set_dir['max_index']), 10)
        self.x = numpy.arange(0, n, 1)
        self.ax.clear()
        # 重新创建annot对象
        self.annot = self.ax.annotate(
            "", xy=(0, 0), xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->")
        )
        self.ax.scatter(self.x, self.y, label=command)
        self.ax.set_title(command)
        self.ax.legend()
        self.annot.set_visible(False)
        self.draw()
        logger.debug("update_image done")

    def hover(self, event):
        if event.inaxes == self.ax:
            # 获取鼠标位置
            x, y = event.xdata, event.ydata
            # 查找最近的点
            if x is not None and y is not None:
                index = (numpy.abs(self.x - x)).argmin()
                self.annot.xy = (self.x[index], self.y[index])
                self.annot.set_text(f'n : {self.x[index]}\na[n] : {self.y[index]}')
                self.annot.set_visible(True)
                self.draw()
        else:
            self.annot.set_visible(False)
            self.draw()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("数列计算器")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个中心小部件
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建布局
        v_layout = QtWidgets.QVBoxLayout(central_widget)
        h_layout = QtWidgets.QHBoxLayout(central_widget)

        #输入框
        self.lineEdit = QtWidgets.QLineEdit(central_widget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 10, 560, 100))
        self.lineEdit.setObjectName("answer_input")
        self.lineEdit.setText("a[n-1] + a[n-2]")
        h_layout.addWidget(self.lineEdit)

        #输入公式按钮
        Button_input = QtWidgets.QPushButton("更新图像", self)
        Button_input.clicked.connect(self.update_image)
        h_layout.addWidget(Button_input)

        #切换模式按钮
        Button_setting = QtWidgets.QPushButton("打开设置", self)
        #初始化状态

        Button_setting.clicked.connect(self.open_setting)

        self.button_setting = Button_setting
        h_layout.addWidget(self.button_setting)

        # 创建 Matplotlib 画布并添加到布局
        self.canvas = MplCanvas(self)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.canvas)

        self.settings_page = SettingsPage()

    def update_image(self):
        command = self.lineEdit.text()
        print(command)
        self.canvas.update_image(command)
        self.update()

    def open_setting(self):
        self.settings_page.show()


class SettingsPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置")
        self.setGeometry(100, 100, 300, 200)

        main_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("公式模式")

        h1_layout = QtWidgets.QHBoxLayout()

        set_dir["mode"] = 1
        set_dir["possible_mode"] = [1, 2]
        ''' 
            1为递推式，2为通项公式
        '''
        self.mode_Button = QtWidgets.QPushButton("递推式")
        self.mode_Button.clicked.connect(self.change_mode)
        h1_layout.addWidget(label)
        h1_layout.addWidget(self.mode_Button)

        h2_layout = QtWidgets.QHBoxLayout()
        h2_label = QtWidgets.QLabel("初始项(以空格隔开)")
        h2_input = QtWidgets.QLineEdit()
        h2_input.setText("1 2")
        h2_layout.addWidget(h2_label)
        h2_layout.addWidget(h2_input)

        self.init_input = h2_input
        set_dir["init_number"] = [1, 2]

        h3_layout = QtWidgets.QHBoxLayout()
        h3_label = QtWidgets.QLabel("计算项数(最小为10)")
        h3_input = QtWidgets.QLineEdit()
        h3_input.setText("10")
        h3_layout.addWidget(h3_label)
        h3_layout.addWidget(h3_input)
        self.max_number_input = h3_input
        set_dir["max_index"] = 10

        main_layout.addLayout(h1_layout)
        main_layout.addLayout(h2_layout)
        main_layout.addLayout(h3_layout)

        self.setLayout(main_layout)

    def change_mode(self):
        now_mode_idx = (set_dir["possible_mode"].index(set_dir["mode"]) + 1) % len(set_dir["possible_mode"])
        set_dir["mode"] = set_dir["possible_mode"][now_mode_idx]
        self.mode_Button.setText({1: "递推式", 2: "通项公式"}[set_dir["mode"]])

    def update_setting(self):
        try:
            set_dir["init_number"] = list(map(float, self.init_input.text().split(" ")))
        except Exception as e:
            logger.error(f"初始化初始项数组 : {e}")
        try:
            set_dir["max_index"] = max(int(self.max_number_input.text()), 10)
        except Exception as e:
            logger.error(f"最大项数设置出错 : {e}")

    def closeEvent(self, a0):
        self.update_setting()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

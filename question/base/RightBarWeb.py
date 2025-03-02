import logging
import sys, os
from PyQt6.QtCore import QObject, pyqtSlot, Qt, QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# 用于通信的QObject子类
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view : QWebEngineView | None = None  # 用于保存WebEngineView的引用
        self.question_list : dict[int : tuple[str, str]] = {1 : ("1", "1"), 2 : ("2", "2"), 3 : ("3", "3"), 4 : ("4", "4"), 5 : ("5", "5")}
        self.main_question_connect = None
        self.get_tag = None
        self.base_html = open(r"question\site\rightBar.html", "r", encoding="utf-8").read()

    @pyqtSlot(str)
    def handle_tag(self, tag):
        """处理来自JavaScript的标签"""
        logger.debug(f"Received tag: {tag}")

        # 根据不同的tag生成不同内容
        assert self.view is not None
        assert callable(self.main_question_connect)
        assert callable(self.get_tag)
        tags = []
        try:
            self.main_question_connect(int(tag))
            tags = " ".join(self.get_tag(int(tag)))
        except ValueError as e:
            self.main_question_connect(tag)
            tags = " ".join(self.get_tag(tag))

        self.view.setHtml(self.base_html
                          .replace("[replaced-site1]", self.question_list[1][0])
                          .replace("[replaced-site2]", self.question_list[2][0])
                          .replace("[replaced-site3]", self.question_list[3][0])
                          .replace("[replaced-site4]", self.question_list[4][0])
                          .replace("[replaced-site5]", self.question_list[5][0])
                          .replace("[replaced-site1-title]", self.question_list[1][1])
                          .replace("[replaced-site2-title]", self.question_list[2][1])
                          .replace("[replaced-site3-title]", self.question_list[3][1])
                          .replace("[replaced-site4-title]", self.question_list[4][1])
                          .replace("[replaced-site5-title]", self.question_list[5][1])
                          .replace("[replaced-tags]", tags)
                          )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化WebEngineView
        self.view = QWebEngineView()
        self.setCentralWidget(self.view)

        # 创建通信桥接对象
        self.bridge = Bridge()
        self.bridge.view = self.view  # 传递view引用

        # 设置WebChannel
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)  # 注册对象到JavaScript
        self.view.page().setWebChannel(self.channel)

        # 初始化HTML内容
        initial_html = open(r"../site/rightBar.html", "r", encoding="utf-8").read()

        self.view.setHtml(initial_html)
        self.setWindowTitle("Tag Navigation Demo")
        self.resize(800, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

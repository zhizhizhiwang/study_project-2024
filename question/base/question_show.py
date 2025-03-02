import sys
import os
from PyQt6 import QtCore, QtWidgets, QtGui, QtWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
from question.base import Questions, Calculator, RightBarWeb
import logging
from functools import singledispatch

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')

DEBUG = -1
RELEASE = 0

status = -1

if status == DEBUG:
    logger.setLevel(logging.DEBUG)
elif status == RELEASE:
    logger.setLevel(logging.INFO)


def convert_to_html(md_text):
    """将Markdown+LaTeX转换为包含MathJax的HTML"""
    html_content = markdown.markdown(
        md_text,
        extensions=['pymdownx.arithmatex'],
        extension_configs={
            'pymdownx.arithmatex': {
                'generic': True  # 使用通用TeX格式（\(...\)和\[...\]）
            }
        }
    )
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
        <script>
        MathJax = {{
            tex: {{
                inlineMath: [['\\(', '\\)']],
                displayMath: [['\\[', '\\]']],
                processEscapes: true
            }},
            options: {{
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
            }}
        }};
        </script>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            .MathJax {{ 
                font-size: 1.1em !important; 
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """


class HomeWindow(QtWidgets.QMainWindow):
    question_answer: str | None
    question_analysis: str | None

    def __init__(self, parent : QtWidgets.QMainWindow ,file_name : str | None = None):
        super().__init__(parent)  # 调用父类的__init__

        self.calculator = Calculator.MainWindow()

        self.setWindowTitle("练习")
        self.setObjectName("MainWindow")
        self.resize(803, 598)
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 741, 501))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.show_layout_h = QtWidgets.QHBoxLayout()
        self.show_layout_h.setObjectName("show_layout_h")
        self.question_show = QWebEngineView()
        font = QtGui.QFont()
        font.setFamily("Maple Mono SC NF")
        self.question_show.setFont(font)
        self.question_show.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.question_show.setAutoFillBackground(False)
        self.question_show.setObjectName("question_show")
        self.show_layout_h.addWidget(self.question_show, 3,
                                     QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        self.question_lib = Questions.QuestionsManager().load_lib(r"题型预测/question.json")

        """右侧栏目相关"""
        self.rightBar = QWebEngineView()
        self.bridge = RightBarWeb.Bridge()
        self.bridge.view = self.rightBar
        self.bridge.main_question_connect = self.load_question
        self.bridge.get_tag = self.get_tag

        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject('bridge', self.bridge)  # 注册对象到JavaScript
        self.rightBar.page().setWebChannel(self.channel)

        self.rightBar.setHtml(open(r"question/site/rightBar.html", "r", encoding="utf-8").read())
        self.rightBar.setObjectName("rightBar")
        self.show_layout_h.addWidget(self.rightBar, 1)
        """----------------------------------------------------"""

        self.show_layout_h.setStretch(0, 3)
        self.show_layout_h.setStretch(1, 1)

        self.verticalLayout.addLayout(self.show_layout_h)

        self.horizontalWidget = QtWidgets.QWidget(parent=self.verticalLayoutWidget)
        self.horizontalWidget.setObjectName("horizontalWidget")

        self.input_layout_h = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.input_layout_h.setObjectName("input_layout_h")
        self.answer_input = QtWidgets.QLineEdit(parent=self.horizontalWidget)
        self.answer_input.setObjectName("answer_input")
        self.input_layout_h.addWidget(self.answer_input)
        self.setup_button = QtWidgets.QPushButton(parent=self.horizontalWidget)
        self.setup_button.setObjectName("setup_button")
        self.setup_button.setText("提交")
        self.setup_button.clicked.connect(self.check_answer)
        self.input_layout_h.addWidget(self.setup_button)
        self.verticalLayout.addWidget(self.horizontalWidget)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 803, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")

        self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.question_answer = None
        self.question_analysis = None
        self.question_tags = []
        self.set_content("欢迎使用")

        """菜单"""
        self.debug_control = self.menubar.addMenu("其他功能")
        self.right_bar_action = QtGui.QAction("切换右侧栏状态")
        self.right_bar_action.setStatusTip("切换右侧栏状态")
        self.right_bar_action.triggered.connect(self.change_right_bar_action)
        self.debug_control.addAction(self.right_bar_action)

        self.open_question = QtGui.QAction("从文件加载题目")
        self.open_question.triggered.connect(self.open_question_from_file)
        self.debug_control.addAction(self.open_question)

        self.open_calculator = QtGui.QAction("打开数列计算器")
        self.open_calculator.triggered.connect(self.calculator.show)

        self.menubar.addAction(self.open_calculator)
        self.setCentralWidget(self.centralwidget)

        if file_name is not None:
            self.bridge.handle_tag(file_name)

    def set_content(self, md_text):
        """更新显示内容"""
        html = convert_to_html(md_text)
        self.question_show.setHtml(html)

    def load_question(self, filename : int | str):
        if isinstance(filename, int):
            question_input = self.question_lib[filename]
            print(question_input.surface)
            self.set_content(question_input.surface + "\n\n" + " ".join(question_input.options))
            _, _, self.question_answer, self.question_analysis, self.question_tags = question_input.unpack()
            same_tag_list : list[Questions.Question] = []
            for tag in question_input.tags:
                same_tag_list += \
                    [q for _, q in self.question_lib.questions_dir.values()
                     if tag in q.tags and
                     q.question_id != question_input.question_id]
            for i in range(min(5, len(same_tag_list))):
                self.bridge.question_list[i + 1] = [str(same_tag_list[i].question_id), " ".join(same_tag_list[i].tags)]

        elif isinstance(filename, str):
            try:
                question_input = Questions.Question().load_from_file(filename)
            except Exception as e:
                logger.error(f"加载题目文件失败{e}")
                logger.error(f"当前目录{os.getcwd()}")
                raise e
            print(question_input.surface)
            self.set_content(question_input.surface + "\n\n" + " \n\n ".join(question_input.options))
            _, _, self.question_answer, self.question_analysis, self.question_tags = question_input.unpack()
            same_tag_list: list[Questions.Question] = []
            for tag in question_input.tags:
                same_tag_list += [q for _, q in self.question_lib.questions_dir.values() if tag in q.tags and q.question_id != question_input.question_id]
            for i in range(min(5, len(same_tag_list))):
                self.bridge.question_list[i + 1] = [str(same_tag_list[i].question_id), " ".join(same_tag_list[i].tags)]
        else:
            logger.error("load_question参数不匹配")

    def get_tag(self, filename : int | str) -> list[str]:
        if isinstance(filename, int):
            question_input = self.question_lib[filename]
            return question_input.tags
        elif isinstance(filename, str):
            try:
                question_input = Questions.Question().load_from_file(filename)
                return question_input.tags
            except Exception as e:
                logger.error(f"加载题目标签失败{e}")
                logger.error(f"当前目录{os.getcwd()}")
                return []
        else:
            logger.error("get_tag参数不匹配")
            return []

    def check_answer(self):
        if self.question_answer is not None:
            if str(self.answer_input.text()) == str(self.question_answer):
                self.statusbar.showMessage("回答正确", 2000)
            else:
                self.statusbar.showMessage("回答错误", 2000)
        else:
            logger.warning("在未加载问题时提交答案")
            self.statusbar.showMessage("未加载问题", 1000)

    def change_right_bar_action(self):
        if self.rightBar.isVisible():
            self.rightBar.hide()
        else:
            self.rightBar.show()

    def open_question_from_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择题目json文件", os.path.abspath('..'), "Json文件 (*.json)")
        if filename:
            self.load_question(filename)
        else:
            logger.error(f"加载题目失败, 选择了{filename}, {_}")

    def right_bar_url_change(self, url : QtCore.QUrl):
        site = url.toString()
        logger.debug(f"url: {site}")
        try:
            question = Questions.Question().load_from_file(site)
        except Exception as e:
            logger.error("无法读取文件", e)
            self.rightBar.setHtml(open(r"../site/404.html", "r", encoding="utf-8").read().replace("[replaced-error-str]", e.__repr__()))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    window.bridge.handle_tag(r"question\example_question.json")
    sys.exit(app.exec())

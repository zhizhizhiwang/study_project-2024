import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
from base import Questions, Calculator
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


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

    def __init__(self):
        super().__init__()  # 调用父类的__init__
        self.setWindowTitle("Home Page")
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

        self.tableView = QtWidgets.QTableView(parent=self.verticalLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.show_layout_h.addWidget(self.tableView, 1)

        self.tableView.hide()

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
        self.set_content("欢迎使用")

    def set_content(self, md_text):
        """更新显示内容"""
        html = convert_to_html(md_text)
        self.question_show.setHtml(html)

    def load_question(self, question: Questions.Problem):
        print(question.surface)
        self.set_content(question.surface)
        _, self.question_answer, self.question_analysis = question.unpack()

    def check_answer(self):
        if self.question_answer is not None:
            if str(self.answer_input.text()) == str(self.question_answer):
                self.statusbar.showMessage("回答正确", 2000)
            else:
                self.statusbar.showMessage("回答错误", 2000)
        else:
            logger.debug("在未加载问题时提交答案")
            self.statusbar.showMessage("未加载问题", 1000)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    window.load_question(Questions.example_question)
    sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.resize(803, 598)
        self.add_app(main.HomeWindow(),"home")

    def add_app(self, app, tab_name):
        """将现有应用添加到标签栏."""
        # 创建一个新的QWidget作为标签页的内容
        tab_content = QWidget()
        layout = QVBoxLayout(tab_content)

        # 获取app的中央小部件并添加到新的标签页
        central_widget = app.centralWidget()  # 获取中央小部件
        layout.addWidget(central_widget)  # 将其添加到新标签页的布局中
        app.setParent(tab_content) # 设置父窗口，很重要。

        # 将新的QWidget标签页添加到标签栏
        self.tab_widget.addTab(tab_content, tab_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

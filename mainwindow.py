# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(803, 598)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 741, 501))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("show_layout_h")
        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
        self.lineEdit_4.setMinimumSize(QtCore.QSize(400, 400))
        self.lineEdit_4.setMaximumSize(QtCore.QSize(16777215, 22))
        self.lineEdit_4.setSizeIncrement(QtCore.QSize(0, 0))
        self.lineEdit_4.setBaseSize(QtCore.QSize(1, 1))
        font = QtGui.QFont()
        font.setFamily("Maple Mono SC NF")
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.lineEdit_4.setAutoFillBackground(False)
        self.lineEdit_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("question_show")
        self.horizontalLayout_4.addWidget(self.lineEdit_4, 0, QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.tableView = QtWidgets.QTableView(parent=self.verticalLayoutWidget)
        self.tableView.setObjectName("rightBar")
        self.horizontalLayout_4.addWidget(self.tableView)
        self.horizontalLayout_4.setStretch(0, 3)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalWidget = QtWidgets.QWidget(parent=self.verticalLayoutWidget)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setObjectName("input_layout_h")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.horizontalWidget)
        self.lineEdit.setObjectName("answer_input")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(parent=self.horizontalWidget)
        self.pushButton.setObjectName("setup_button")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.horizontalWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 803, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))

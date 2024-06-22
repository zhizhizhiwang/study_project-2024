from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication([])
window = QMainWindow()

label = QLabel("Hello PyQt!")
window.setCentralWidget(label)

window.show()
app.exec()

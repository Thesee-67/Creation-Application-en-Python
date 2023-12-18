import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLabel

class First(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.resize(250, 150)

        self.second_button = QPushButton("Open Second Window")
        grid.addWidget(self.second_button)

        self.second_button.clicked.connect(self.pageSuiv)
        self.second_window = None  # Garder une référence à la deuxième fenêtre

    def pageSuiv(self):
        if not self.second_window or not self.second_window.isVisible():
            self.second_window = Second()
            self.second_window.show()

class Second(QWidget):
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)
        self.label = QLabel("Hello, World !")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    first = First()
    first.show()
    sys.exit(app.exec_())


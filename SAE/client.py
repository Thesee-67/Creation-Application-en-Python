import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QTextCursor, QColor
import socket

class MessageSignal(QObject):
    message_received = pyqtSignal(str)

class ClientThread(QThread):
    def __init__(self, client_socket, message_signal, flag):
        super().__init__()
        self.client_socket = client_socket
        self.signal = message_signal
        self.flag = flag

    def run(self):
        while self.flag[0]:
            try:
                reply = self.client_socket.recv(1024).decode()
                self.signal.message_received.emit(reply)

            except (socket.error, socket.timeout):
                self.show_error_dialog("La connexion avec le serveur a été perdue.")
                break

    def show_error_dialog(self, error_message):
        self.flag[0] = False
        self.client_socket.close()
        # Afficher un message d'erreur
        QMessageBox.critical(None, "Erreur", error_message)

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GuiGui Chat")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.chat_text = QTextEdit(self)
        self.chat_text.setReadOnly(True)
        self.chat_text.setStyleSheet("background-color: #F0F0F0; color: black;")

        self.message_entry = QLineEdit(self)
        self.send_button = QPushButton("Envoyer", self)
        self.send_button.setStyleSheet("background-color: #25D366; color: white;")
        self.send_button.clicked.connect(self.send_message)

        top_layout = QVBoxLayout()
        top_layout.addWidget(self.chat_text)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_entry)
        bottom_layout.addWidget(self.send_button)

        layout = QVBoxLayout(self.central_widget)
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        self.client_socket = socket.socket()
        self.flag = [True]
        self.receive_thread = ClientThread(self.client_socket, MessageSignal(), self.flag)
        self.receive_thread.signal.message_received.connect(self.append_message)

        self.connect_to_server()

        # Afficher un message d'information
        QMessageBox.information(self, "Bienvenue sur GuiGui Chat", "Bienvenue ! Pour quitter, tapez 'bye' ou fermez la fenêtre.")

    def connect_to_server(self):
        host = "127.0.0.1"
        port = 10000

        try:
            self.client_socket.connect((host, port))
            self.receive_thread.start()

        except Exception as e:
            self.show_error_dialog(f"Impossible de se connecter au serveur : {e}")

    @pyqtSlot(str)
    def append_message(self, message):
        self.chat_text.append(message)
        cursor = self.chat_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_text.setTextCursor(cursor)

    @pyqtSlot()
    def send_message(self):
        message = self.message_entry.text()
        if message.lower() == "bye":
            self.flag[0] = False
            self.client_socket.send(message.encode())
            self.receive_thread.join()
            self.client_socket.close()
            sys.exit()
        else:
            self.client_socket.send(message.encode())
            self.message_entry.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())
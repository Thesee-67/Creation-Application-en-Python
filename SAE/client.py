import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket

class MessageSignal(QObject):
    message_received = pyqtSignal(str)

class ClientThread(QThread):
    def __init__(self, client_socket, message_signal, flag, wait_condition, mutex):
        super().__init__()
        self.client_socket = client_socket
        self.signal = message_signal
        self.flag = flag
        self.wait_condition = wait_condition
        self.mutex = mutex

    def run(self):
        while self.flag[0]:
            try:
                reply = self.client_socket.recv(1024).decode()
                if not reply:
                    break  # Arrêter la boucle si la connexion est fermée
                self.signal.message_received.emit(reply)

            except (socket.error, socket.timeout):
                break

        # Pause pour laisser le temps au thread principal de gérer la fermeture de la fenêtre
        self.msleep(100)

        # Signaliser à la condition d'attente que le thread se termine
        with QMutexLocker(self.mutex):  # Utilisez QMutexLocker pour garantir la libération du mutex
            self.wait_condition.wakeAll()

        self.client_socket.close()  # Fermer la socket

    def show_error_dialog(self, error_message):
        self.flag[0] = False
        self.client_socket.close()

        # Utiliser QMetaObject.invokeMethod pour demander au thread principal d'afficher le message d'erreur
        QMetaObject.invokeMethod(self, "_show_error_dialog", Qt.QueuedConnection, Q_ARG(str, error_message))

    @pyqtSlot(str)
    def _show_error_dialog(self, error_message):
        # Afficher un message d'erreur depuis le thread principal
        QMessageBox.critical(None, "Erreur", error_message)

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GuiGui Chat")
        self.setGeometry(100, 100, 600, 400)

        # Ajout de l'en-tête avec le titre et les informations sur l'application
        header_label = QLabel("<h1 style='color: white;'>GUIGUI Tchat Compagnie</h1>"
                              "<p style='color: white;'>Une application de messagerie conviviale.</p>", self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("background-color: #3498db;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.chat_text = QTextEdit(self)
        self.chat_text.setReadOnly(True)
        self.chat_text.setStyleSheet("background-color: #F0F0F0; color: black;")

        self.message_entry = QLineEdit(self)
        self.send_button = QPushButton("Envoyer", self)
        self.send_button.setStyleSheet("background-color: #25D366; color: white;")
        self.send_button.clicked.connect(self.send_message)

        self.change_button = QPushButton("Changer de Topic", self)
        self.change_button.setStyleSheet("background-color: #FFD600; color: black;")
        self.change_button.clicked.connect(self.change_topic)

        info_button = QPushButton(self)
        info_button.setIcon(QIcon("SAE/Question.png"))  # Remplacez "information_icon.png" par le chemin de votre icône d'information
        info_button.clicked.connect(self.show_instructions)

        top_layout = QVBoxLayout()
        top_layout.addWidget(header_label)  # Ajout de l'en-tête
        top_layout.addWidget(self.chat_text)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_entry)
        bottom_layout.addWidget(self.send_button)
        bottom_layout.addWidget(self.change_button)
        bottom_layout.addWidget(info_button)

        layout = QVBoxLayout(self.central_widget)
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        self.mutex = QMutex()  # Créez un objet QMutex

        self.client_socket = socket.socket()
        self.flag = [True]
        self.wait_condition = QWaitCondition()  # Condition d'attente pour le thread
        self.receive_thread = ClientThread(self.client_socket, MessageSignal(), self.flag, self.wait_condition, self.mutex)
        self.receive_thread.signal.message_received.connect(self.append_message)

        self.connect_to_server()

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
        self.client_socket.send(message.encode())
        self.message_entry.clear()

    @pyqtSlot()
    def change_topic(self):
        new_topic = self.message_entry.text()
        if new_topic.lower() in {"général", "blabla", "comptabilité", "informatique", "marketing"}:
            self.client_socket.send(f"change:{new_topic}".encode())
            self.message_entry.clear()
        else:
            QMessageBox.warning(self, "Erreur de topic", "Le topic spécifié n'est pas valide.")

    def show_instructions(self):
        # Fonction pour afficher les instructions
        instructions = ("Bienvenue sur GuiGui Chat!\n"
                        "Utilisez le bouton 'Changer de Topic' pour changer de salon du tchat.\n")
        QMessageBox.information(self, "Instructions", instructions)

    def closeEvent(self, event):
        # Redéfinir la méthode closeEvent pour gérer la fermeture de la fenêtre
        self.flag[0] = False  # Arrêter le thread de réception
        self.client_socket.close()  # Fermer la socket

        # Attendre que le thread de réception se termine
        with QMutexLocker(self.mutex):  # Utilisez QMutexLocker pour garantir la libération du mutex
            self.wait_condition.wakeAll()
        self.receive_thread.quit()  # Ajouter cette ligne pour quitter le thread de manière propre
        self.receive_thread.wait()  # Attendre que le thread de réception se termine

        event.accept()  # Accepter la fermeture de la fenêtre

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())


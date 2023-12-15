import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMutex, QMutexLocker, QWaitCondition, QMetaObject

class MessageSignal(QObject):
    message_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

class ClientThread(QThread):
    def __init__(self, client_socket, message_signal, flag, wait_condition, mutex):
        super().__init__()
        self.client_socket = client_socket
        self.signal = message_signal
        self.flag = flag
        self.wait_condition = wait_condition
        self.mutex = mutex

    def run(self):
        try:
            while self.flag[0]:
                reply = self.client_socket.recv(1024).decode()
                if not reply:
                    break  # Arrêter la boucle si la connexion est fermée
                self.signal.message_received.emit(reply)

        except (socket.error, socket.timeout) as e:
            self.signal.error_occurred.emit(f"Erreur de connexion : {e}")

        finally:
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

class TopicDialog(QDialog):
    def __init__(self, options, parent=None):
        super(TopicDialog, self).__init__(parent)

        self.setWindowTitle("Changer de Topic")
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
            }
            QLabel {
                color: white;
            }
            QComboBox {
                background-color: #34495E;
                color: white;
                min-width: 300px;
            }
            QPushButton {
                background-color: black;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: black;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Choisissez un nouveau topic:")
        label.setStyleSheet("color: white;")

        self.comboBox = QComboBox()
        self.comboBox.addItems(options)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(self.comboBox)
        layout.addWidget(buttonBox)

    def selectedTopic(self):
        return self.comboBox.currentText()


class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super(ProfileDialog, self).__init__(parent)

        self.setWindowTitle("Créer un Profil")
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #34495E;
                color: white;
            }
            QPushButton {
                background-color: black;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: black;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Bienvenue ! Veuillez compléter votre profil.")
        label.setStyleSheet("color: white;")

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Entrez votre nom d'utilisateur")

        self.nom_entry = QLineEdit(self)
        self.nom_entry.setPlaceholderText("Entrez votre nom")

        self.prenom_entry = QLineEdit(self)
        self.prenom_entry.setPlaceholderText("Entrez votre prénom")

        self.identifiant_entry = QLineEdit(self)
        self.identifiant_entry.setPlaceholderText("Entrez votre identifiant")

        self.mot_de_passe_entry = QLineEdit(self)
        self.mot_de_passe_entry.setPlaceholderText("Entrez votre mot de passe")
        self.mot_de_passe_entry.setEchoMode(QLineEdit.Password)

        self.create_button = QPushButton("Créer le Profil", self)
        self.create_button.clicked.connect(self.create_profile)

        layout.addWidget(label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.nom_entry)
        layout.addWidget(self.prenom_entry)
        layout.addWidget(self.identifiant_entry)
        layout.addWidget(self.mot_de_passe_entry)
        layout.addWidget(self.create_button)

    def create_profile(self):
        username = self.username_entry.text()
        nom = self.nom_entry.text()
        prenom = self.prenom_entry.text()
        identifiant = self.identifiant_entry.text()
        mot_de_passe = self.mot_de_passe_entry.text()

        if username and nom and prenom and identifiant and mot_de_passe:
            profile_message = f"create_profile:{username}:{nom}:{prenom}:{identifiant}:{mot_de_passe}"
            self.accept()
            self.parent().client_socket.send(profile_message.encode())
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GuiGui TChat")
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
        info_button.setIcon(QIcon("SAE\Image\Question.png"))  # Remplacez "information_icon.png" par le chemin de votre icône d'information
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
        self.receive_thread.signal.message_received.connect(self.handle_message)

        self.connect_to_server()

    def connect_to_server(self):
        host = "127.0.0.2"
        port = 10000

        try:
            self.client_socket.connect((host, port))
            self.receive_thread.start()

        except Exception as e:
            self.show_error_dialog(f"Impossible de se connecter au serveur : {e}")

    def handle_message(self, message):
        # Gérer le message de profil
        if message.lower().startswith("profile:"):
            _, profile_info = message.split(":", 1)
            QMessageBox.information(self, "Profil", profile_info)
        else:
            self.chat_text.append(message)
            cursor = self.chat_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_text.setTextCursor(cursor)

    def send_message(self):
        message = self.message_entry.text()
        self.client_socket.send(message.encode())
        self.message_entry.clear()

    def change_topic(self):
        # Créer une instance de TopicDialog
        topic_dialog = TopicDialog(["Général", "BlaBla", "Comptabilité", "Informatique", "Marketing"], self)
        result = topic_dialog.exec_()

        if result == QDialog.Accepted:
            new_topic = topic_dialog.selectedTopic()
            self.client_socket.send(f"change:{new_topic}".encode())
            self.message_entry.clear()

    def show_instructions(self):
        # Créer une instance de QMessageBox
        info_box = QMessageBox(self)

        # Appliquer le style uniquement à cette instance
        info_box.setStyleSheet("""
            QMessageBox {
                background-color: orange; /* Fond blanc */
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)

        # Configurer le texte et le titre de la boîte de dialogue
        info_box.setWindowTitle("Informations")
        info_box.setText("Bienvenue sur GuiGui Tchat!<br><br>"
                        "Utilisez le bouton 'Changer de Topic' pour changer de salon du tchat.<br><br>"
                        "Quand vous recevez le message d'arrêt du serveur, veuillez fermer l'application.<br><br>"
                        "Si vous avez des problèmes, n'hésitez pas à contacter l'équipe technique via l'adresse mail suivante <a href='mailto:olivier.guittet@uha.fr'>olivier.guittet@uha.fr</a>.<br><br>"
                        "Cordialement l'équipe technique.")

        # Ajouter un bouton "OK" à la boîte de dialogue
        info_box.addButton(QMessageBox.Ok)

        # Afficher la boîte de dialogue
        info_box.exec_()

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



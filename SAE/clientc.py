import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMutex, QMutexLocker, QWaitCondition, QMetaObject
import re
import time
import json

        
class MessageSignal(QObject):
    message_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    update_users_list = pyqtSignal(list)  # Ajout du signal pour la mise à jour de la liste des utilisateurs


class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)

        self.setWindowTitle("Connexion au Serveur")
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

        self.resize(400, 200)  # Ajuster la taille de la fenêtre

        layout = QVBoxLayout(self)

        label_ip = QLabel("Adresse IP du Client:")
        label_ip.setStyleSheet("color: white;")
        self.ip_entry = QLineEdit(self)
        self.ip_entry.setPlaceholderText("Entrez l'adresse IP")

        label_port = QLabel("Port du Client:")
        label_port.setStyleSheet("color: white;")
        self.port_entry = QLineEdit(self)
        self.port_entry.setPlaceholderText("Entrez le port")

        self.connect_button = QPushButton("Se Connecter", self)
        self.connect_button.clicked.connect(self.accept)

        layout.addWidget(label_ip)
        layout.addWidget(self.ip_entry)
        layout.addWidget(label_port)
        layout.addWidget(self.port_entry)
        layout.addWidget(self.connect_button)

    def is_valid_ip(self, host):
        # Utilisez une expression régulière pour valider le format de l'adresse IP
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        return bool(ip_pattern.match(host))
    
    def is_valid_port(self, port_text):
        if not port_text.isdigit():
            return False

        port = int(port_text)
        return 0 < port < 65536  # Le port doit être un entier entre 1 et 65535
    
    def get_connection_info(self):
        ip = self.ip_entry.text()
        port_text = self.port_entry.text()

        # Valider le format de l'adresse IP
        if not self.is_valid_ip(ip):
            return None, None

        # Valider le format du port
        if not self.is_valid_port(port_text):
            return None, None

        port = int(port_text)
        return ip, port

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
                if reply.startswith("users:"):
                    # Si le message commence par "users:", c'est une mise à jour des utilisateurs
                    users_info = json.loads(reply[6:])  # Pour extraire la partie JSON du message
                    self.signal.update_users_list.emit(users_info)
                else:
                    # Sinon, c'est un message normal
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

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GuiGui TChat")
        self.setGeometry(100, 100, 600, 400)
        self.showMaximized()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        header_label = QLabel("<h1 style='color: white;'>GUIGUI Tchat Compagnie</h1>"
                              "<p style='color: white;'>Une application de messagerie conviviale.</p>", self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("background-color: #3498db;")

        # Zone principale du chat
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
        info_button.setIcon(QIcon("SAE\Image\Question.png"))
        info_button.clicked.connect(self.show_instructions)

        # Layout pour la zone principale du chat
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(header_label)
        chat_layout.addWidget(self.chat_text)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_entry)
        bottom_layout.addWidget(self.send_button)
        bottom_layout.addWidget(self.change_button)
        bottom_layout.addWidget(info_button)

        chat_layout.addLayout(bottom_layout)

        profil_button = QPushButton("Profil", self)
        profil_button.clicked.connect(self.afficher_profil) 

        # Créer une étiquette pour le titre
        titre_label = QLabel("Clients Connectés", self)
        titre_label.setStyleSheet("background-color: #3498db; color: white;")
        titre_label.setAlignment(Qt.AlignCenter)

        # Liste des utilisateurs
        self.users_list_widget = QListWidget(self)
        self.users_list_widget.setStyleSheet("background-color: #F0F0F0;")
        self.users_list_widget.setMinimumWidth(150)
        self.users_list_widget.setMaximumWidth(200)
        self.users_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Layout pour la liste des utilisateurs
        users_layout = QVBoxLayout()
        users_layout.addWidget(profil_button)
        users_layout.addWidget(titre_label)
        users_layout.addWidget(self.users_list_widget)

        # Layout principal pour la fenêtre
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.addLayout(chat_layout)
        main_layout.addLayout(users_layout)

        self.mutex = QMutex()  # Créez un objet QMutex
        self.client_socket = socket.socket()
        self.flag = [True]
        self.wait_condition = QWaitCondition()  # Condition d'attente pour le thread
        self.receive_thread = ClientThread(self.client_socket, MessageSignal(), self.flag, self.wait_condition, self.mutex)
        self.receive_thread.signal.message_received.connect(self.handle_message)
        self.receive_thread.signal.update_users_list.connect(self.update_users_list_widget)
        self.connect_to_server()

    def connect_to_server(self):
        while True:
            connection_dialog = ConnectionDialog(self)
            result = connection_dialog.exec_()

            if result != QDialog.Accepted:
                # L'utilisateur a appuyé sur "Annuler" ou fermé la fenêtre, quitter la boucle
                QMessageBox.information(self, "Information", "Veuillez fermer l'application.")
                break

            host, port = connection_dialog.get_connection_info()

            # Valider l'adresse IP et le port
            if host is None or port is None:
                QMessageBox.warning(self, "Erreur", "Adresse IP ou port invalide. Veuillez réessayer.")
                continue  # Afficher à nouveau la boîte de dialogue en cas d'erreur
            elif not self.valid_ip(host, port):
                QMessageBox.warning(self, "Erreur", "Adresse IP ou port invalide. Veuillez réessayer.")
                continue  # Afficher à nouveau la boîte de dialogue en cas d'erreur

            try:
                self.client_socket.connect((host, port))
                self.receive_thread.start()
                break  # Sortir de la boucle si la connexion réussit

            except Exception as e:
                error_message = f"Impossible de se connecter au serveur : {e}"
                self.show_error_dialog(error_message)

    def afficher_profil():

        return

    def valid_ip(self, ip, port_text):
        try:
            # Valider le format de l'adresse IP
            socket.inet_pton(socket.AF_INET, ip)

            # Valider le port
            if not str(port_text).isdigit():
                return False

            port = int(port_text)

            # Tester la connexion avec l'adresse IP et le port
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)  # Temps d'attente pour la connexion
            test_socket.connect((ip, port))
            test_socket.close()

            return True

        except (socket.error, ValueError):
            return False

        
    def valid_port(self, port):
        try:
            port = int(port)
            return 0 < port < 65536  # Le port doit être un entier entre 1 et 65535
        except ValueError:
            return False
    

    def show_error_dialog(self, error_message):
        self.flag[0] = False
        self.client_socket.close()

        # Utiliser QMetaObject.invokeMethod pour demander au thread principal d'afficher le message d'erreur
        QMetaObject.invokeMethod(self, "_show_error_dialog", Qt.QueuedConnection, Q_ARG(str, error_message))

    @pyqtSlot(str)
    def _show_error_dialog(self, error_message):
        # Afficher un message d'erreur depuis le thread principal
        QMessageBox.critical(None, "Erreur", error_message)

    @pyqtSlot(list)
    def update_users_list_widget(self, users_info):
        self.users_list_widget.clear()

        for user, status in users_info:
            item = QListWidgetItem(f"{user} - {'Connecté' if status == 1 else 'Déconnecté'}")
            self.users_list_widget.addItem(item)

        # Mise à jour du statut pour tous les utilisateurs
        for index in range(self.users_list_widget.count()):
            item = self.users_list_widget.item(index)
            username = item.text().split(" - ")[0]
            status = "Connecté" if any((user, stat) == (username, 1) for user, stat in users_info) else "Déconnecté"
            item.setText(f"{username} - {status}")



    @pyqtSlot(str)
    def handle_message(self, message):
        if message.startswith("users:"):
            # Mettez à jour la liste des utilisateurs connectés
            users_info = json.loads(message[6:])  # Pour extraire la partie JSON du message
            self.update_users_list_widget(users_info)
        else:
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
        # Demander confirmation à l'utilisateur
        reply = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir quitter?', 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Utilisateur a confirmé la fermeture

            # Arrêter le thread de réception
            self.flag[0] = False
            self.client_socket.close()  # Fermer la socket

            # Attendre que le thread de réception se termine
            with QMutexLocker(self.mutex):  # Utilisez QMutexLocker pour garantir la libération du mutex
                self.wait_condition.wakeAll()

            self.receive_thread.finished.connect(self.receive_thread.quit)  # Connecter le signal finished à la méthode quit
            self.receive_thread.quit()  # Ajouter cette ligne pour quitter le thread de manière propre
            self.receive_thread.wait()  # Attendre que le thread de réception se termine

            event.accept()  # Accepter la fermeture de la fenêtre
        else:
            # Utilisateur a annulé la fermeture
            event.ignore()  # Ignorer la fermeture de la fenêtre

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())



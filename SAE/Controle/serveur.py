import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket

class ClientReceiver(QThread):
    message_received = pyqtSignal(str, 'PyQt_PyObject')
    disconnect_requested = pyqtSignal('PyQt_PyObject')  

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.message_received.emit(message, self.client_socket)
                if message == "deco-server":
                    self.disconnect_requested.emit(self.client_socket)
                    break
        except Exception as e:
            print(f"Erreur de réception : {e}")
        finally:
            self.client_socket.close()

class ServerThread(QThread):
    connection_established = pyqtSignal()
    server_stopped = pyqtSignal()

    def __init__(self, ip, port, max_clients, text_output):
        super().__init__()
        self.ip = ip
        self.port = port
        self.max_clients = max_clients
        self.server_socket = None
        self.clients = {}
        self.text_output = text_output

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.max_clients)

        self.connection_established.emit()

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients[client_socket] = {"address": client_address, "connected": True}

                receive_thread = ClientReceiver(client_socket)
                receive_thread.message_received.connect(self.message_received)
                receive_thread.disconnect_requested.connect(self.disconnect_client)
                receive_thread.start()

            except Exception as e:
                print(f"Erreur lors de l'acceptation d'un client : {e}")
                self.server_stopped.emit()
                break

    def message_received(self, message, client_socket):
        print(f"Reçu d'un client : {message}")
        QMetaObject.invokeMethod(self.text_output, 'append', Qt.QueuedConnection, Q_ARG(str, f'Message reçu : {message}'))

    def disconnect_client(self, client_socket):
        try:
            if client_socket in self.clients and self.clients[client_socket]["connected"]:
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                self.clients[client_socket]["connected"] = False
        except Exception as e:
            print(f"Erreur lors de la déconnexion d'un client : {e}")

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            for client_socket in self.clients:
                self.disconnect_client(client_socket)
            self.server_stopped.emit()

class ServerInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Serveur Tchat')

        self.label_ip = QLabel('Serveur:')
        self.entry_ip = QLineEdit('0.0.0.0')

        self.label_port = QLabel('Port:')
        self.entry_port = QLineEdit('10000')

        self.label_max_clients = QLabel('Nombre de clients maximum:')
        self.entry_max_clients = QLineEdit('5')

        self.start_stop_button = QPushButton('Démarrage du serveur')
        self.start_stop_button.clicked.connect(self.toggle_server)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)

        self.quit_button = QPushButton('Quitter')
        self.quit_button.clicked.connect(self.close)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.addRow('Serveur', self.entry_ip)
        form_layout.addRow('Port:', self.entry_port)
        form_layout.addRow('Nombre de clients maximum:', self.entry_max_clients)

        layout.addLayout(form_layout)

        layout.addWidget(self.start_stop_button)
        layout.addWidget(self.text_output)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

        self.server_thread = None

    def toggle_server(self):
        try:
            if self.server_thread is None or not self.server_thread.isRunning():
                ip = self.entry_ip.text()
                port = int(self.entry_port.text())
                max_clients = int(self.entry_max_clients.text())

                print(f"Starting server on {ip}:{port} with max clients: {max_clients}")

                self.server_thread = ServerThread(ip, port, max_clients, self.text_output)
                self.server_thread.connection_established.connect(self.server_started)
                self.server_thread.server_stopped.connect(self.server_stopped)
                self.server_thread.start()

                self.start_stop_button.setText('Arrêt du serveur')
            else:
                self.server_thread.stop_server()
        except ValueError:
            QMessageBox.warning(self, 'Erreur', 'Veuillez entrer des valeurs valides pour le port et le nombre de clients.')
        except Exception as e:
            print(f"Erreur lors du démarrage/arrêt du serveur : {e}")

    def server_started(self):
        self.text_output.append('Le serveur est démarré et en attente de connexions.')

    def server_stopped(self):
        self.text_output.append('Le serveur a été arrêté.')
        self.start_stop_button.setText('Démarrage du serveur')

    def closeEvent(self, event):
        if self.server_thread is not None and self.server_thread.isRunning():
            self.server_thread.stop_server()

def main():
    app = QApplication(sys.argv)
    window = ServerInterface()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

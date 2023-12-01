import socket
import threading
import time

def receive_messages(client_socket, flag):
    while flag[0]:
        try:
            reply = client_socket.recv(1024).decode()
            print("J'ai reçu le message:", reply)

            # Ajouter une vérification pour le message "stop"
            if reply.lower() == "stop":
                print("Reçu un message 'stop'. Envoi de 'bye' au serveur.")
                print("Veuillez appuez sur entrée pour vous déconnectez")
                client_socket.send("bye".encode())

        except (socket.error, socket.timeout):
            # Gérer les erreurs de socket
            break

def client_logic():
    host = "127.0.0.2"
    port = 10000
    flag = [True]

    try:
        client_socket = socket.socket()
        client_socket.connect((host, port))

        # Démarrer un thread pour la réception des messages du serveur
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, flag))
        receive_thread.start()

        while flag[0]:
            message = input("Entrez le message à envoyer (ou 'bye' pour quitter le serveur): ")

            client_socket.send(message.encode())

            if message == "bye":
                print("Demande de déconnexion envoyée au serveur. Fermeture du client.")
                flag[0] = False
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()

        receive_thread.join()  # Attendre que le thread de réception se termine

    except (socket.error, socket.timeout) as e:
        print(f"Erreur de socket : {e}")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")

if __name__ == '__main__':
    client_logic()

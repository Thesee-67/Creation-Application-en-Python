import socket
import threading

def receive_messages(client_socket, flag):
    while flag[0]:
        try:
            reply = client_socket.recv(1024).decode()
            print(f"\n{reply}")

        except (socket.error, socket.timeout):
            # Gérer les erreurs de socket
            break

def client_logic():
    host = "127.0.0.1"
    port = 10000
    flag = [True]

    try:
        client_socket = socket.socket()
        client_socket.connect((host, port))

        # Démarrer un thread pour la réception des messages du serveur
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, flag))
        receive_thread.start()

        # Demander au client de choisir le topic
        topic = input("Choisissez le topic (1 ou 2): ")
        client_socket.send(topic.encode())

        while flag[0]:
            message = input("Entrez le message à envoyer (ou 'bye' pour quitter le serveur): ")

            if message.lower() == "bye":
                print("Demande de déconnexion envoyée au serveur. Fermeture du client.")
                flag[0] = False
            else:
                client_socket.send(message.encode())

        receive_thread.join()  # Attendre que le thread de réception se termine

    except (socket.error, socket.timeout) as e:
        print(f"Erreur de socket : {e}")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")

    finally:
        client_socket.close()

if __name__ == '__main__':
    client_logic()

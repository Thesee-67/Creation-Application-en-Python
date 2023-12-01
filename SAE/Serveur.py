import socket
import threading

def broadcast_message(message, clients, topic):
    for client_conn, client_topic in clients:
        if client_topic == topic:
            try:
                client_conn.send(message.encode())
            except (socket.error, socket.timeout):
                # Gérer les erreurs de socket
                continue
def handle_client(conn, address, flag_lock, flag, clients):
    reply = "J'ai bien reçu votre message"
    flag2 = True

    try:
        # Demander au client de choisir un topic
        conn.send("Entrez le numéro du topic auquel vous souhaitez participer (1 ou 2) : ".encode())
        topic_choice = conn.recv(1024).decode()

        if topic_choice not in {"1", "2"}:
            conn.send("Le topic spécifié n'existe pas.".encode())
            conn.close()
            return

        conn.send(f"Bienvenue dans le topic {topic_choice} !".encode())

        with flag_lock:
            clients.append((conn, topic_choice))

        while flag2:
            message = conn.recv(1024).decode()
            if message.lower() == "bye":
                print(f"Client {address} a quitté le topic {topic_choice}.")
                break

            broadcast_message(f"[Topic {topic_choice}] Client {address}: {message}", clients, topic_choice)

    except ConnectionResetError:
        print(f"La connexion avec {address} a été réinitialisée par le client.")
    except Exception as e:
        print(f"Une exception s'est produite avec {address}: {e}")
    finally:
        # Retirer le client de la liste lorsqu'il se déconnecte
        with flag_lock:
            clients.remove((conn, topic_choice))
            conn.close()  # Fermer la connexion du client

# Reste du code inchangé

def server_shell(flag_lock, flag, clients):
    while flag[0]:
        command = input("Entrez 'stop' pour arrêter le serveur: ")
        if command.lower() == "stop":
            with flag_lock:
                flag[0] = False
            for client_conn, _ in clients:
                try:
                    client_conn.send("bye".encode())
                    # Attendre avant de fermer la connexion pour donner au client le temps de traiter le message
                    client_conn.recv(1024)
                    client_conn.close()
                except (socket.error, socket.timeout):
                    # Gérer les erreurs de socket
                    continue
            print("Arrêt du serveur et déconnexion des clients.")
            break  # Ajouter cette ligne pour sortir de la boucle

if __name__ == '__main__':
    port = 10000
    flag = [True]
    flag_lock = threading.Lock()
    client_threads = []  # Liste pour stocker les threads clients
    clients = []

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print("Serveur en attente de connexions...")

    # Créer un thread pour gérer le shell du serveur
    shell_thread = threading.Thread(target=server_shell, args=(flag_lock, flag, clients))
    shell_thread.start()

    try:
        while flag[0]:
            conn, address = server_socket.accept()
            print(f"Connexion établie avec {address}")

            # Créer un thread pour gérer la connexion client
            client_thread = threading.Thread(target=handle_client, args=(conn, address, flag_lock, flag, clients))
            client_thread.start()

            # Ajouter le client à la liste des clients
            with flag_lock:
                clients.append((conn, ""))  # Ajouter un espace réservé pour le topic, à remplacer lors de la sélection du topic
            client_threads.append(client_thread)

    except KeyboardInterrupt:
        print("\nFermeture du serveur suite à une interruption clavier.")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")
    finally:
        # Attendre que tous les threads clients se terminent avant de fermer le serveur
        for thread in client_threads:
            thread.join()
        shell_thread.join()  # Attendre que le thread du shell se termine
        server_socket.close()

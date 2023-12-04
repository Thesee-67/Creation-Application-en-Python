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
    flag2 = True
    current_topic = ""

    try:
        while True:
            # Demander au client de choisir un topic
            conn.send("Entrez le numéro du topic auquel vous souhaitez participer (Général, BlaBla, Comptabilité, Informatique ou Marketing) :".encode())
            topic_choice = conn.recv(1024).decode()

            if topic_choice in {"Général", "BlaBla", "Comptabilité", "Informatique", "Marketing"}:
                current_topic = topic_choice
                break  # Sortir de la boucle si le topic est valide

            conn.send("Le topic spécifié n'existe pas. Veuillez réessayer.".encode())

        conn.send(f"Bienvenue dans le topic {current_topic} !".encode())

        with flag_lock:
            clients.append((conn, current_topic))

        while flag2:
            message = conn.recv(1024).decode()

            if message.lower().startswith("change:"):
                new_topic = message.split(":")[1].strip()
                if new_topic in {"Général", "BlaBla", "Comptabilité", "Informatique", "Marketing"}:
                    with flag_lock:
                        clients.remove((conn, current_topic))
                        clients.append((conn, new_topic))
                    current_topic = new_topic
                    # Envoyer un message de changement de topic uniquement au client concerné
                    conn.send(f"Vous avez changé de topic. Bienvenue dans le topic {current_topic} !".encode())
                else:
                    conn.send("Le topic spécifié n'est pas valide. Veuillez réessayer.".encode())
            elif message.lower() == "bye":
                print(f"Client {address} a quitté le topic {current_topic}.")
                with flag_lock:
                    clients.remove((conn, current_topic))
                break

            # Exclure les messages de changement de topic du chat
            if not message.lower().startswith("change:"):
                broadcast_message(f"[Topic {current_topic}] Client {address}: {message}", clients, current_topic)

    except ConnectionResetError:
        print(f"La connexion avec {address} a été réinitialisée par le client.")
    except Exception as e:
        print(f"Une exception s'est produite avec {address}: {e}")
    finally:
        # Fermer la connexion du client
        conn.close()

def server_shell(flag_lock, flag, clients):
    while flag[0]:
        command = input("Entrez 'kill' pour arrêter le serveur: ")
        if command.lower() == "kill":
            with flag_lock:
                flag[0] = False
            for client_conn, _ in clients:
                try:
                    client_conn.send("Le serveur doit s'arrêter. Veuillez nous excuser pour la gêne occasionnée. Veuillez fermer l'application en appuyant sur la croix".encode())
                    client_conn.close()
                except (socket.error, socket.timeout):
                    continue
            print("Arrêt du serveur et déconnexion des clients.")
            break

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
        server_socket.settimeout(1.0)  # Définir une temporisation sur le socket

        while flag[0]:
            try:
                conn, address = server_socket.accept()
                print(f"Connexion établie avec {address}")

                # Créer un thread pour gérer la connexion client
                client_thread = threading.Thread(target=handle_client, args=(conn, address, flag_lock, flag, clients))
                client_thread.start()

                # Ajouter le client à la liste des clients
                with flag_lock:
                    clients.append((conn, ""))  # Ajouter un espace réservé pour le topic, à remplacer lors de la sélection du topic
                client_threads.append(client_thread)

            except socket.timeout:
                # Cela permet au serveur de vérifier périodiquement si la commande "stop" a été donnée
                pass

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

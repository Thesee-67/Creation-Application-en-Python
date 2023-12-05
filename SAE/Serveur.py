import socket
import threading
import mysql.connector

# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '04/11/17',
    'database': 'sae_r309'
}

def get_server_credentials():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # Sélectionner les informations de connexion du serveur
    cursor.execute("SELECT login, mot_de_passe FROM serveur LIMIT 1")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result

def check_server_credentials(login, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si les identifiants du serveur sont valides
    cursor.execute("SELECT id FROM serveur WHERE login = %s AND mot_de_passe = %s", (login, password))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

def save_server_credentials(login, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Insérer les identifiants du serveur dans la base de données
    cursor.execute("INSERT INTO serveur (login, mot_de_passe) VALUES (%s, %s)", (login, password))
    connection.commit()

    cursor.close()
    connection.close()

def authenticate_shell():
    credentials = get_server_credentials()

    if not credentials:
        print("Aucun identifiant de serveur trouvé. Veuillez enregistrer de nouveaux identifiants.")
        login = input("Entrez le login du serveur : ")
        password = input("Entrez le mot de passe du serveur : ")
        save_server_credentials(login, password)
        print("Nouveaux identifiants enregistrés. Redémarrez le serveur.")
        return False

    login_attempt = 0
    while True:
        login = input("Entrez le login du serveur : ")
        password = input("Entrez le mot de passe du serveur : ")

        if check_server_credentials(login, password):
            print("Authentification réussie.")
            break
        else:
            print("Identifiants incorrects. Veuillez réessayer.")
            login_attempt += 1

        if login_attempt >= 10000:
            print("Trop de tentatives échouées. Fermeture de la connexion.")
            return False

    return True

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
        print(f"Connexion établie avec {address}.")

        topic_choice_valid = False

        while not topic_choice_valid:
            conn.send("Entrez le nom du premier topic auquel vous souhaitez participer (Général, BlaBla, Comptabilité, Informatique ou Marketing) :".encode())
            first_topic_choice = conn.recv(1024).decode()

            if first_topic_choice in {"Général", "BlaBla", "Comptabilité", "Informatique", "Marketing"}:
                current_topic = first_topic_choice
                with flag_lock:
                    clients.append((conn, current_topic))
                    conn.send(f"Bienvenue dans le topic {current_topic} !".encode())
                topic_choice_valid = True  # Sortir de la boucle si le topic est valide
            else:
                conn.send("Le premier topic spécifié n'est pas valide. Veuillez réessayer.".encode())

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
    if not authenticate_shell():
        return

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

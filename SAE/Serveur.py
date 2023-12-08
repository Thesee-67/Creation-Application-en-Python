import socket
import threading
import mysql.connector
import re

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

def is_valid_email(email):
    email_pattern = re.compile(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$')
    return bool(re.match(email_pattern, email))

def check_user_credentials(identifiant, mot_de_passe):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si l'identifiant et le mot de passe correspondent à un utilisateur dans la base de données
    cursor.execute("SELECT id FROM utilisateurs WHERE identifiant = %s AND mot_de_passe = %s", (identifiant, mot_de_passe))
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

def user_exists(pseudo):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si l'utilisateur existe dans la base de données
    cursor.execute("SELECT id FROM utilisateurs WHERE pseudo = %s", (pseudo,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

def insert_user_profile(pseudo, nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Insérer le profil utilisateur dans la base de données
        cursor.execute("INSERT INTO utilisateurs (pseudo, nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               (pseudo, nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip))
        connection.commit()
        print(f"Inserted user profile for {pseudo} successfully.")
    except Exception as e:
        print(f"Error inserting user profile for {pseudo}: {e}")
        connection.rollback()

    cursor.close()
    connection.close()

def get_client_ip(conn):
    # Obtenez l'adresse IP du client à partir de la connexion
    client_address = conn.getpeername()[0]
    return client_address

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

        if login_attempt >= 3:
            print("Trop de tentatives échouées. Fermeture de la connexion.")
            return False

    return True

def get_pseudo_from_client(conn, identifiant):
    connection = mysql.connector.connect(**db_config)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT pseudo FROM utilisateurs WHERE identifiant = %s", (identifiant,))
        result = cursor.fetchone()

        if result:
            pseudo = result[0]
        else:
            pseudo = "Pseudo_inconnu"  # Utilisez le pseudo par défaut si rien n'est trouvé
    finally:
        connection.close()

    return pseudo

def save_message_to_db(identifiant, message_texte, current_topic, address):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Insérer le message dans la base de données
        cursor.execute("INSERT INTO messages (utilisateur_identifiant, message_texte, topic, adresse_ip) VALUES (%s, %s, %s, %s)",
                       (identifiant, message_texte, current_topic, address))
        connection.commit()
    except Exception as e:
        print(f"Error saving message to database: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def broadcast_message(message, clients, topic):
    for client_conn, client_topic in clients:
        if client_topic == topic:
            try:
                # Remplacez l'adresse IP par le pseudo
                pseudo = get_pseudo_from_client(client_conn, identifiant)

                # Construire le message avec le pseudonyme mais sans la partie spécifique
                message_with_pseudo = f"[Topic {topic}] {pseudo}:{message}"

                # Envoyer le message au client
                client_conn.send(message_with_pseudo.encode())
            except (socket.error, socket.timeout):
                # Gérer les erreurs de socket
                continue

def create_user_profile(conn):
    global identifiant
    conn.send("Bienvenue !\n".encode())

    while True:
        conn.send("Avez-vous déjà un compte ? (Oui/Non): ".encode())
        response = conn.recv(1024).decode().lower()

        if response == "oui":
            # Demander à l'utilisateur de saisir son identifiant et son mot de passe
            login_attempt = 0
            while login_attempt < 3:
                conn.send("Entrez votre identifiant : ".encode())
                identifiant = conn.recv(1024).decode()

                conn.send("Entrez votre mot de passe : ".encode())
                mot_de_passe = conn.recv(1024).decode()

                # Vérifier que l'identifiant et le mot de passe sont des chaînes non vides
                if not identifiant or not mot_de_passe:
                    conn.send("Identifiant et mot de passe invalides. Réessayez.\n".encode())
                    login_attempt += 1
                    continue

                # Ajouter la vérification des identifiants dans la base de données
                if check_user_credentials(identifiant, mot_de_passe):
                    conn.send("Authentification réussie ! Bienvenue.\n".encode())
                    break
                else:
                    conn.send("Identifiants incorrects. Réessayez.\n".encode())
                    login_attempt += 1

                if login_attempt >= 3:
                    conn.send("Trop de tentatives échouées. Fermeture de la connexion. Veuillez fermer l'application.\n".encode())
                    conn.close()
                    return

            break 

        elif response == "non":
            conn.send("Veuillez compléter votre profil.\n".encode())

            conn.send("Entrez votre pseudo : ".encode())
            pseudo = conn.recv(1024).decode()

            conn.send("Entrez votre nom : ".encode())
            nom = conn.recv(1024).decode()

            conn.send("Entrez votre prénom : ".encode())
            prenom = conn.recv(1024).decode()

            while True:
                conn.send("Adresse e-mail : ".encode())
                adresse_mail = conn.recv(1024).decode()

                # Vérifier l'adresse e-mail
                if not is_valid_email(adresse_mail):
                    conn.send("Adresse e-mail invalide. Veuillez réessayer.\n".encode())
                    continue

                break

            while True:
                conn.send("Entrez votre identifiant : ".encode())
                identifiant = conn.recv(1024).decode()

                conn.send("Entrez votre mot de passe : ".encode())
                mot_de_passe = conn.recv(1024).decode()


                # Ajouter la vérification des identifiants dans la base de données
                if user_exists(identifiant):
                    conn.send("Identifiant déjà utilisé. Réessayez avec un autre identifiant.\n".encode())
                else:
                    insert_user_profile(pseudo, nom, prenom, adresse_mail, identifiant, mot_de_passe, get_client_ip(conn))
                    conn.send(f"Profil créé avec succès !\n"
                      f"Vous avez entré les informations suivantes :\n"
                      f"Pseudo: {pseudo}\n"
                      f"Nom: {nom}\n"
                      f"Prénom: {prenom}\n"
                      f"Adresse e-mail: {adresse_mail}\n"
                      f"Identifiant: {identifiant}\n".encode())
                    conn.send(f"Bienvenue {pseudo}!\n".encode())
                    break
            break  
        else:
            conn.send("Réponse non valide. Veuillez répondre par 'Oui' ou 'Non'.\n".encode())

def handle_client(conn, address, flag_lock, flag, clients,):
    flag2 = True
    current_topic = ""

    try:
        print(f"Connexion établie avec {address}.")

        pseudo = conn.recv(1024).decode()
        user_exists_flag = user_exists(pseudo)

        # Envoyer "Bienvenue" ici, avant de vérifier si le profil existe
        conn.send("Bienvenue !\n".encode())

        if user_exists_flag:
            # Si le profil existe, envoyer un message et continuer normalement
            conn.send("Bienvenue ! Vous avez déjà un profil.\n".encode())
        else:
            # Si le profil n'existe pas, créer un profil
            create_user_profile(conn)

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
            else:
                # Enregistrez le message dans la base de données
                save_message_to_db(identifiant, message, current_topic, address[0])

            # Exclure les messages de changement de topic du chat
            if not message.lower().startswith("change:"):
                broadcast_message(f"{message}", clients, current_topic)

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

import socket
import threading
import mysql.connector
import re
from datetime import datetime, timedelta 


# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '04/11/17',
    'database': 'sae_r309'
}



def apply_sanction(conn, identifiant, type_sanction, flag_lock=None):
    if type_sanction == "ban":
        save_sanction_to_db(identifiant, conn.getpeername()[0], type_sanction,flag_lock)
        conn.send("Vous avez été banni. Déconnexion en cours...".encode())
        conn.close()
    elif type_sanction == "kick":
        save_sanction_to_db(identifiant, conn.getpeername()[0], type_sanction,flag_lock)
        conn.send("Vous avez été kické. Déconnexion en cours...".encode())
        conn.close()

def save_sanction_to_db(identifiant, adresse_ip, type_sanction, duree=None, flag_lock=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    if flag_lock:
        with flag_lock:
            try:
                if type_sanction == "kick" and duree is not None:
                    # Si c'est un kick, calculez la date de fin de sanction (1 heure)
                    current_time = datetime.now()
                    date_fin_sanction = current_time + timedelta(hours=1)
                    cursor.execute(
                        "INSERT INTO sanctions (identifiant, adresse_ip, type_sanction,date_sanction, date_fin_sanction) VALUES (%s, %s, %s, %s, %s, %s)",
                        (identifiant, adresse_ip, type_sanction, current_time,date_fin_sanction)
                    )
                elif type_sanction == "ban":
                    cursor.execute(
                        "INSERT INTO sanctions (identifiant, adresse_ip, type_sanction,) VALUES (%s, %s, %s, %s)",
                        (identifiant, adresse_ip, type_sanction,)
                    )

                connection.commit()
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de la sanction dans la base de données : {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()

def is_user_banned(identifiant):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id FROM sanctions WHERE identifiant = %s AND type_sanction = 'ban'", (identifiant,))
        result = cursor.fetchone()
        return result is not None

    except Exception as e:
        print(f"Erreur lors de la vérification du bannissement : {e}")
        return False

    finally:
        cursor.close()
        connection.close()


def is_user_kicked(identifiant):
    # Vérifier si l'utilisateur est kické
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Sélectionner la sanction de type "kick" la plus récente pour l'utilisateur
        cursor.execute("SELECT date_fin_sanction FROM sanctions WHERE identifiant = %s AND type_sanction = 'kick' ORDER BY date_fin_sanction DESC LIMIT 1", (identifiant,))
        result = cursor.fetchone()

        if result is not None:
            date_fin_sanction = result[0]
            current_time = datetime.now()

            # Comparer la date de fin de sanction avec l'heure actuelle
            if current_time < date_fin_sanction:
                return True
    except Exception as e:
        print(f"Erreur lors de la vérification du statut de kick de l'utilisateur : {e}")
    finally:
        cursor.close()
        connection.close()

    return False

def close_client_connection(identifiant, flag_lock):
    # Fonction pour fermer la connexion du client
    if flag_lock:
        with flag_lock:
            if identifiant in dico2:
                conn = dico2[identifiant]
                conn.send("Vous avez été sanctionné. Déconnexion en cours...".encode())
                conn.close()

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

def user_exists(identifiant):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si l'utilisateur existe dans la base de données
    cursor.execute("SELECT id FROM utilisateurs WHERE identifiant = %s", (identifiant,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

def save_authorization(identifiant, topic):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Insérer l'autorisation dans la base de données
        cursor.execute("INSERT INTO autorisation (utilisateur_identifiant, topic) VALUES (%s, %s)",
                       (identifiant, topic))
        connection.commit()
    except Exception as e:
        print(f"Error saving authorization to database: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def insert_user_profile(nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Insérer le profil utilisateur dans la base de données
        cursor.execute("INSERT INTO utilisateurs (nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip) VALUES (%s, %s, %s, %s, %s, %s)",
               (nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip))
        connection.commit()
        print(f"Inserted user profile for {identifiant} successfully.")
    except Exception as e:
        print(f"Error inserting user profile for {identifiant}: {e}")
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

        if login_attempt >= 100:
            print("Trop de tentatives échouées. Fermeture de la connexion.")
            return False

    return True

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

def is_user_authorized(identifiant, nouveau_topic):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si l'utilisateur a une autorisation pour le topic spécifié
    cursor.execute("SELECT id FROM autorisation WHERE utilisateur_identifiant = %s AND topic = %s",
                   (identifiant, nouveau_topic))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None


def broadcast_message(message, clients, topic, identifiant):
    for client_conn, client_topic in clients:
        if client_topic == topic:
            try:
                # Remplacez l'adresse IP par le pseudo

                # Utiliser l'identifiant ou "Inconnu" s'il est manquant
                identifiant_affichage = identifiant if identifiant else "Inconnu"

                # Construire le message avec le pseudonyme mais sans la partie spécifique
                message_with_pseudo = f"[Topic {topic}] Pseudo:{identifiant_affichage}: {message}"

                # Envoyer le message au client
                client_conn.send(message_with_pseudo.encode())
            except (socket.error, socket.timeout):
                # Gérer les erreurs de socket
                continue


def create_user_profile(conn):
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

                dico[conn] = identifiant
                dico2[identifiant] = conn

                if is_user_banned(identifiant):
                    conn.send("Vous êtes banni. Contactez l'administrateur pour plus d'informations.\n".encode())
                    conn.close()
                    return
                

                if is_user_kicked(identifiant):
                    conn.send(f"Vous avez été kické. Attendez la fin de la sanction pour vous reconnecter.\n".encode())
                    conn.close()
                    return

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
                dico[conn] = identifiant
                dico2[identifiant] = conn

                conn.send("Entrez votre mot de passe : ".encode())
                mot_de_passe = conn.recv(1024).decode()


                # Ajouter la vérification des identifiants dans la base de données
                if user_exists(identifiant):
                    conn.send("Identifiant déjà utilisé. Réessayez avec un autre identifiant.\n".encode())
                else:
                    insert_user_profile(nom, prenom, adresse_mail, identifiant, mot_de_passe, get_client_ip(conn))
                    conn.send(f"Profil créé avec succès !\n"
                      f"Vous avez entré les informations suivantes :\n"
                      f"Nom: {nom}\n"
                      f"Prénom: {prenom}\n"
                      f"Adresse e-mail: {adresse_mail}\n"
                      f"Identifiant: {identifiant}\n".encode())
                    save_authorization(identifiant, "Général")
                    conn.send(f"Bienvenue {identifiant}!\n".encode())
                    break
            break  
        else:
            conn.send("Réponse non valide. Veuillez répondre par 'Oui' ou 'Non'.\n".encode())

def handle_client(conn, address, flag_lock, flag, clients):
    flag2 = True
    
    
    try:
        print(f"Connexion établie avec {address}.")

        create_user_profile(conn)

        choix_topic_valide = False

        with flag_lock:
            topic_actuel = "Général"
            identifiant = dico[conn]
            dico3[identifiant] = topic_actuel
            clients.append((conn, topic_actuel))
            conn.send(f"Bienvenue dans le salon {topic_actuel} !".encode())

        while flag2:
            message = conn.recv(1024).decode()

            if message.lower().startswith("change:"):
                identifiant = dico[conn]
                nouveau_topic = message.split(":")[1].strip()
                if nouveau_topic not in Salons_topic:
                    conn.send("Sujet invalide. Veuillez choisir parmi les sujets disponibles.".encode())
                elif nouveau_topic == "BlaBla":
                    if is_user_authorized(identifiant, nouveau_topic):
                        conn.send(f"Vous avez changé de salon. Bienvenue dans le salon {nouveau_topic} !".encode())             
                        # Vérifier si une demande en attente existe déjà pour cet utilisateur
                        topic_actuel = dico3[identifiant]
                        with flag_lock:
                            clients.remove((conn, topic_actuel))
                            clients.append((conn, nouveau_topic))
                        dico3[identifiant] = nouveau_topic
                    else:
                        topic_actuel = dico3[identifiant]
                    # Accepter automatiquement le changement vers "BlaBla" et enregistrer dans la table d'autorisations
                        with flag_lock:
                            clients.remove((conn, topic_actuel))
                            clients.append((conn, nouveau_topic))
                        dico3[identifiant] = nouveau_topic
                        conn.send(f"Vous avez changé de salon. Bienvenue dans le salon {nouveau_topic} !".encode())
                        save_authorization(identifiant, nouveau_topic)
                elif is_user_authorized(identifiant, nouveau_topic):
                    conn.send(f"Vous avez changé de salon. Bienvenue dans le salon {nouveau_topic} !".encode())             
                    # Vérifier si une demande en attente existe déjà pour cet utilisateur
                    topic_actuel = dico3[identifiant]
                    with flag_lock:
                        clients.remove((conn, topic_actuel))
                        clients.append((conn, nouveau_topic))
                    dico3[identifiant] = nouveau_topic
                else:
                    if identifiant in demandes_en_attente:
                        conn.send("Vous avez déjà une demande en attente. Veuillez patienter.".encode())
                    else:
                    # Ajouter la demande en attente
                        demandes_en_attente[identifiant] = nouveau_topic
                        conn.send(f"Votre demande de rejoindre {nouveau_topic} est en attente d'approbation.".encode())


            elif message.lower() == "bye":
                topic = dico3[identifiant]
                print(f"Client {address} a quitté le salon {topic}.")
                with flag_lock:
                    clients.remove((conn, topic))
                break
            else:
                # Enregistrez le message dans la base de données
                identifiant = dico[conn]
                topic = dico3[identifiant]
                save_message_to_db(identifiant, message, topic, address[0])
                # Exclure les messages de changement de sujet du chat
                if not message.lower().startswith("change:"):
                    broadcast_message(f"{message}", clients, topic, identifiant)

    except ConnectionResetError:
        print(f"La connexion avec {address} a été réinitialisée par le client.")
    except Exception as e:
        print(f"Une exception s'est produite avec {address} : {e}")
    finally:
        # Fermer la connexion du client
        conn.close()

def server_shell(flag_lock, flag, clients,):
    if not authenticate_shell():
        return

    while flag[0]:
        commande = input("Entrez 'kill' pour arrêter le serveur : ")
        if commande.lower() == "kill":
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
        elif commande.lower() == "showdemande":
            print("Demandes en attente :")
            for identifiant, topic in demandes_en_attente.items():
                print(f"- {identifiant} : {topic}")
        elif commande.lower().startswith("accept@"):
            parts = commande.split("@")
            if len(parts) == 2:
                user_and_text = parts[1].split(":")
                identifiant = user_and_text[0].strip()  # Supprime les espaces autour du nom d'utilisateur
                if identifiant in demandes_en_attente:
                    new_topic = demandes_en_attente[identifiant]
                    conn = dico2[identifiant]
                    topic2 = dico3[identifiant]
                    with flag_lock:
                        clients.remove((conn, topic2))
                        clients.append((conn, new_topic))
                    dico3[identifiant] = new_topic
                    save_authorization(identifiant, new_topic)
                    for client_conn, _ in clients:
                        if client_conn == conn:
                            client_conn.send(f"Vous avez changé de salon. Bienvenue dans le salon {new_topic} !".encode())
                            break
                    print(f"La demande de {identifiant} pour rejoindre {new_topic} a été acceptée.")
                    # Supprimer la demande en attente après l'acceptation
                    del demandes_en_attente[identifiant]
                else:
                    print(f"Aucune demande en attente pour {identifiant}.")
            else:
                print("Commande incorrecte. Utilisez 'accept@identifiant'.")
        elif commande.lower().startswith("refuser@"):
            parts = commande.split("@")
            if len(parts) == 2:
                identifiant = parts[1].strip()  # Supprime les espaces autour du nom d'utilisateur
                if identifiant in demandes_en_attente:
                    # Répondre au client refusé
                    conn = dico2[identifiant]
                    conn.send("Votre demande a été refusée.".encode())
                    # Supprimer la demande en attente après le refus
                    del demandes_en_attente[identifiant]
                    print(f"La demande de {identifiant} a été refusée.")
                else:
                    print(f"Aucune demande en attente pour {identifiant}.")
            else:
                print("Commande incorrecte. Utilisez 'refuser@identifiant'.")
        elif commande.lower().startswith("ban@"):
            parts = commande.split("@")
            if len(parts) == 2:
                identifiant = parts[1].strip()  # Obtenez l'identifiant depuis la commande
                conn = dico2[identifiant]
                apply_sanction(conn, identifiant, 'ban', flag_lock=flag_lock)
                print(f"{identifiant} a été banni.")
            else:
                print("Commande incorrecte. Utilisez 'ban@identifiant'.")
        elif commande.lower().startswith("kick@"):
            parts = commande.split("@")
            if len(parts) == 2:
                identifiant = parts[1].strip()
                conn = dico2[identifiant]
                apply_sanction(conn, identifiant, 'kick',flag_lock=flag_lock)
                print(f"Sanction de 1h appliquée à {identifiant}.")
            else:
                print("Commande incorrecte. Utilisez 'kick@identifiant'.")
        else:
            print("Commande non reconnue. Utilisez 'kill', 'showdemande' ou 'accept@identifiant'.")


if __name__ == '__main__':
    port = 10000
    flag = [True]
    flag_lock = threading.Lock()
    client_threads = []  # Liste pour stocker les threads clients
    clients = []
    dico3 = {}
    dico = {}
    dico2 = {}
    demandes_en_attente = {}
    Salons_topic = ["Général","BlaBla","Comptabilité","Informatique","Marketing"]

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print("Serveur en attente de connexions...")

    # Créer un thread pour gérer le shell du serveur
    shell_thread = threading.Thread(target=server_shell, args=(flag_lock, flag, clients,))
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

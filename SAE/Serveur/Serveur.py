import socket
import threading
import mysql.connector
import re
from datetime import datetime, timedelta 
import json
import time
from threading import *

"""
Script principal pour le serveur de chat multi-utilisateurs.

Le script crée un serveur socket qui accepte les connexions des clients, gère les connexions client via des threads,
et offre un shell de commande pour administrer le serveur. Le serveur prend en charge plusieurs fonctionnalités,
telles que le changement de salon, la gestion des sanctions, la demande de profil, et l'envoi d'informations aux clients.

Auteurs :
    - Guittet Olivier

Fonctions :
    - `server_shell(flag_lock, flag, clients)`: Fonction pour le shell du serveur.
    - `handle_client(conn, address, flag_lock, flag, clients)`: Fonction pour gérer la connexion client.
    - `start_send_user_info(clients, flag_lock)`: Fonction pour démarrer l'envoi d'informations utilisateur.
    - `send_user_info(clients, flag_lock)`: Fonction pour envoyer des informations utilisateur.
    - `create_user_profile(conn)`: Fonction pour créer un profil utilisateur.
    - `is_user_banned(identifiant)`: Fonction pour vérifier si un utilisateur est banni.
    - `is_user_kicked(identifiant)`: Fonction pour vérifier si un utilisateur est kické.
    - `check_user_credentials(identifiant, mot_de_passe)`: Fonction pour vérifier les identifiants d'un utilisateur.
    - `is_valid_name(nom)`: Fonction pour vérifier la validité du nom.
    - `is_valid_prenom(prenom)`: Fonction pour vérifier la validité du prénom.
    - `is_valid_email(adresse_mail)`: Fonction pour vérifier la validité de l'adresse e-mail.
    - `is_valid_identifiant(identifiant)`: Fonction pour vérifier la validité de l'identifiant.
    - `is_valid_mot_de_passe(mot_de_passe)`: Fonction pour vérifier la validité du mot de passe.
    - `user_exists(identifiant)`: Fonction pour vérifier si un utilisateur existe.
    - `insert_user_profile(nom, prenom, adresse_mail, identifiant, mot_de_passe, ip)`: Fonction pour insérer un profil utilisateur dans la base de données.
    - `save_authorization(identifiant, topic)`: Fonction pour enregistrer une autorisation dans la table d'autorisations.
    - `save_message_to_db(identifiant, message, topic, ip)`: Fonction pour enregistrer un message dans la base de données.
    - `apply_sanction(conn, identifiant, sanction_type, flag_lock)`: Fonction pour appliquer une sanction (ban ou kick) à un utilisateur.
    - `unban(identifiant)`: Fonction pour lever le ban d'un utilisateur.
    - `unkick(identifiant)`: Fonction pour lever la sanction kick d'un utilisateur.
    - `get_banned_clients()`: Fonction pour obtenir la liste des clients bannis.
    - `get_kicked_clients()`: Fonction pour obtenir la liste des clients kickés.
"""

# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'administrateur',
    'password': 'toto',
    'database': 'sae_r309'
}

def execute_query(query, values=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        connection.commit()
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
    finally:
        cursor.close()
        connection.close()

def get_banned_clients():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT identifiant FROM sanctions WHERE type_sanction = 'ban'")
            result = cursor.fetchall()
            return [row[0] for row in result]
        except mysql.connector.Error as mysql_error:
            print(f"Erreur MySQL lors de la récupération des clients bannis : {mysql_error}")
            return []
        except Exception as e:
            print(f"Erreur inattendue lors de la récupération des clients bannis : {e}")
            return []
        finally:
            cursor.close()
    except mysql.connector.Error as mysql_error:
        print(f"Erreur MySQL lors de la connexion à la base de données : {mysql_error}")
        return []
    except Exception as e:
        print(f"Erreur inattendue lors de la connexion à la base de données : {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()



def get_kicked_clients():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT identifiant, date_sanction FROM sanctions WHERE type_sanction = 'kick'")
            result = cursor.fetchall()
            return [(row[0], row[1]) for row in result]
        except mysql.connector.Error as mysql_error:
            print(f"Erreur MySQL lors de la récupération des clients kickés : {mysql_error}")
            return []
        except Exception as e:
            print(f"Erreur inattendue lors de la récupération des clients kickés : {e}")
            return []
        finally:
            cursor.close()
    except mysql.connector.Error as mysql_error:
        print(f"Erreur MySQL lors de la connexion à la base de données : {mysql_error}")
        return []
    except Exception as e:
        print(f"Erreur inattendue lors de la connexion à la base de données : {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        
def apply_sanction(conn, identifiant, type_sanction, flag_lock=None):
    try:
        if type_sanction == "ban":
            save_sanction_to_db(identifiant, conn.getpeername()[0], type_sanction, flag_lock)
            conn.send("Vous avez été banni. Déconnexion en cours...".encode())
            print(f"{identifiant} c'est fait bannir")
        elif type_sanction == "kick":
            save_sanction_to_db(identifiant, conn.getpeername()[0], type_sanction, flag_lock)
            conn.send("Vous avez été kické. Déconnexion en cours...".encode())
            print(f"{identifiant} c'est fait kick pour 1 heure")
    except Exception as e:
        print(f"Erreur lors de l'application de la sanction : {e}")
    finally:
        try:
            conn.close()
        except Exception as close_error:
            print(f"Erreur lors de la fermeture de la connexion : {close_error}")

def save_sanction_to_db(identifiant, adresse_ip, type_sanction, flag_lock=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    if flag_lock:
        with flag_lock:
            try:
                # Supprimer les sanctions existantes pour cet identifiant et ce type de sanction
                cursor.execute("DELETE FROM sanctions WHERE identifiant = %s AND type_sanction = %s", (identifiant, type_sanction))
                connection.commit()

                if type_sanction == "kick":
                    # Si c'est un kick, calculez la date de fin de sanction (1 heure)
                    current_time = datetime.now()
                    date_fin_sanction = current_time + timedelta(hours=1)
                    cursor.execute(
                        "INSERT INTO sanctions (identifiant, adresse_ip, type_sanction, date_sanction, date_fin_sanction) VALUES (%s, %s, %s, %s, %s)",
                        (identifiant, adresse_ip, type_sanction, current_time, date_fin_sanction)
                    )
                elif type_sanction == "ban":
                    cursor.execute(
                        "INSERT INTO sanctions (identifiant, adresse_ip, type_sanction, date_sanction) VALUES (%s, %s, %s, %s)",
                        (identifiant, adresse_ip, type_sanction, datetime.now())
                    )

                connection.commit()
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de la sanction dans la base de données : {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()

def is_user_banned(identifiant):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT id FROM sanctions WHERE identifiant = %s AND type_sanction = 'ban'", (identifiant,))
            result = cursor.fetchone()
            return result is not None

        except mysql.connector.Error as mysql_error:
            print(f"Erreur MySQL lors de la vérification du bannissement : {mysql_error}")
            return False

        except Exception as e:
            print(f"Erreur inattendue lors de la vérification du bannissement : {e}")
            return False

        finally:
            cursor.close()
    except mysql.connector.Error as mysql_error:
        print(f"Erreur MySQL lors de la connexion à la base de données : {mysql_error}")
        return False
    except Exception as e:
        print(f"Erreur inattendue lors de la connexion à la base de données : {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def unban(identifiant, flag_lock=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM sanctions WHERE identifiant = %s AND type_sanction = 'ban'", (identifiant,))
            rows_deleted = cursor.rowcount
            connection.commit()

            if rows_deleted > 0:
                if flag_lock:
                    with flag_lock:
                        print(f"{identifiant} a été débanni.")
                else:
                    print(f"{identifiant} a été débanni.")
            else:
                print(f"Aucune sanction contre l'identifiant {identifiant}.")

        except mysql.connector.Error as mysql_error:
            print(f"Erreur MySQL lors du débannissement de {identifiant} : {mysql_error}")
        except Exception as e:
            print(f"Erreur inattendue lors du débannissement de {identifiant} : {e}")
        finally:
            cursor.close()

    except mysql.connector.Error as mysql_error:
        print(f"Erreur MySQL lors de la connexion à la base de données : {mysql_error}")
    except Exception as e:
        print(f"Erreur inattendue lors de la connexion à la base de données : {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def unkick(identifiant, flag_lock=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM sanctions WHERE identifiant = %s AND type_sanction = 'kick'", (identifiant,))
            rows_deleted = cursor.rowcount
            connection.commit()

            if rows_deleted > 0:
                if flag_lock:
                    with flag_lock:
                        print(f"{identifiant} a été unkick.")
                else:
                    print(f"{identifiant} a été unkick.")
            else:
                print(f"Aucune sanction contre l'identifiant {identifiant}.")

        except mysql.connector.Error as mysql_error:
            print(f"Erreur MySQL lors de l'unkick de {identifiant} : {mysql_error}")
        except Exception as e:
            print(f"Erreur inattendue lors de l'unkick de {identifiant} : {e}")
        finally:
            cursor.close()

    except mysql.connector.Error as mysql_error:
        print(f"Erreur MySQL lors de la connexion à la base de données : {mysql_error}")
    except Exception as e:
        print(f"Erreur inattendue lors de la connexion à la base de données : {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def info_profile_database(identifiant):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    cursor.execute("SELECT nom, prenom, identifiant, adresse_ip, adresse_mail FROM utilisateurs WHERE identifiant = %s", (identifiant,))
    profile_info = cursor.fetchone()

    cursor.close()
    connection.close()

    return profile_info


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

def update_user_status(identifiant, status):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Mettre à jour le statut de connexion de l'utilisateur
    cursor.execute("UPDATE utilisateurs SET statut = %s WHERE identifiant = %s", (status, identifiant))
    connection.commit()

    cursor.close()
    connection.close()

def check_user_credentials(identifiant, mot_de_passe):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Vérifier si l'identifiant et le mot de passe correspondent à un utilisateur dans la base de données
    cursor.execute("SELECT id FROM utilisateurs WHERE identifiant = %s AND mot_de_passe = %s", (identifiant, mot_de_passe))
    result = cursor.fetchone()

    if result is not None:
        update_user_status(identifiant, 1)

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
        cursor.execute("INSERT INTO utilisateurs (nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip, statut) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               (nom, prenom, adresse_mail, identifiant, mot_de_passe, adresse_ip, 1))
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

def is_valid_name(nom):
    pattern = re.compile(r'^[a-zA-Z]+([ \'-][a-zA-Z]+)*$')
    return bool(re.match(pattern,nom))

def is_valid_prenom(prenom):
    pattern = re.compile(r'^[a-zA-Z]+([ \'-][a-zA-Z]+)*$')
    return bool(re.match(pattern,prenom))

def is_valid_mot_de_passe(mot_de_passe):
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', mot_de_passe))

def is_valid_identifiant(identifiant):
    return bool(re.match(r'^[A-Za-z0-9_-]{4,}$', identifiant))

def send_user_info(clients, flag_lock):
    while not send_user_info_flag.is_set():
        with flag_lock:
            # Récupérer tous les identifiants et leur statut depuis la base de données
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT identifiant, statut FROM utilisateurs")
            users_info = cursor.fetchall()
            connection.close()

            # Convertir les résultats en une liste de tuples (identifiant, statut)
            users_info = [(user_info['identifiant'], user_info['statut']) for user_info in users_info]

        # Vérifier si la liste des utilisateurs est vide
        if not users_info:
            time.sleep(5)
            continue

        users_info_str = json.dumps(users_info)

        # Filtrer les clients actifs avant de les envoyer
        active_clients = [(client, identifiant) for client, identifiant in clients if client.fileno() != -1]

        for client, _ in active_clients:
            try:
                client.send(f"users:{users_info_str}".encode())
            except Exception as e:
                print(f"Erreur lors de l'envoi des informations à {client}: {e}")

        time.sleep(5)

def start_send_user_info(clients, flag_lock):
    global send_user_info_flag
    send_user_info_flag = threading.Event()
    send_user_info_flag.set()  # Mettez le drapeau à l'état "set" pour démarrer la boucle
    send_user_info(clients, flag_lock)

def create_user_profile(conn):
    """
    Crée un profil utilisateur en demandant des informations à l'utilisateur.

    :param conn: Objet de connexion pour le client
    :type conn: socket.socket
    """

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
                conn.send(f"Vous avez rentreé l'identifiant :{identifiant}.\n".encode())

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
            conn.send(f"Vous avez rentrer le nom :{nom}.\n".encode())

            while not is_valid_name(nom):
                conn.send("Format de nom invalide. Veuillez réessayer.\n".encode())
                conn.send("Entrez votre nom : ".encode())
                nom = conn.recv(1024).decode()
                conn.send(f"Vous avez rentrer le nom :{nom}.\n".encode())

            conn.send("Entrez votre prénom : ".encode())
            prenom = conn.recv(1024).decode()
            conn.send(f"Vous avez rentrer le prenom :{prenom}.\n".encode())

            while not is_valid_prenom(prenom):
                conn.send("Format de prénom invalide. Veuillez réessayer.\n".encode())
                conn.send("Entrez votre prénom : ".encode())
                prenom = conn.recv(1024).decode()            
                conn.send(f"Vous avez rentrer le prenom :{prenom}.\n".encode())


            while True:
                conn.send("Adresse e-mail : \n".encode())
                adresse_mail = conn.recv(1024).decode()
                conn.send(f"Vous avez rentrer l'adresse mail :{adresse_mail}.\n".encode())


                # Vérifier l'adresse e-mail
                if not is_valid_email(adresse_mail):
                    conn.send("Adresse e-mail invalide. Veuillez réessayer.\n".encode())
                    continue

                break

            while True:
                conn.send("L'identifiant doit avoir au moins 4 caractères et ne peut contenir que des lettres, des chiffres, des tirets bas (_) et des tirets (-).\n".encode())
                conn.send("Entrez votre identifiant : \n".encode())
                identifiant = conn.recv(1024).decode()
                conn.send(f"Vous avez rentrer l'identifiant :{identifiant}.\n".encode())


                while not is_valid_identifiant(identifiant):
                    conn.send("Format de identifiant invalide. Veuillez réessayer.\n".encode())
                    conn.send("Entrez votre identifiant : \n".encode())
                    identifiant = conn.recv(1024).decode()
                    conn.send(f"Vous avez rentrer l'identifiant :{identifiant}.\n".encode())

                
                dico[conn] = identifiant
                dico2[identifiant] = conn

                conn.send(" Le mot de passe doit avoir au moins 8 caractères, inclure au moins une lettre et au moins un chiffre.\n".encode())
                conn.send("Entrez votre mot de passe : \n".encode())
                mot_de_passe = conn.recv(1024).decode()
                conn.send(f"Vous avez rentrer le mot_de_passe :{mot_de_passe}.\n".encode())

                while not is_valid_mot_de_passe(mot_de_passe):
                    conn.send("Format de mot de passe invalide. Veuillez réessayer.\n".encode())
                    conn.send("Entrez votre mot de passe : \n".encode())
                    mot_de_passe = conn.recv(1024).decode()
                    conn.send(f"Vous avez rentrer le mot_de_passe :{mot_de_passe}.\n".encode())


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
    """
    Gère la connexion d'un client, y compris la création de profil, les changements de salon, et la réception/envoi de messages.

    :param conn: Objet de connexion pour le client
    :type conn: socket.socket
    :param address: Adresse du client
    :type address: tuple
    :param flag_lock: Serrure pour assurer la cohérence entre les threads sur le drapeau
    :type flag_lock: threading.Lock
    :param flag: Drapeau pour contrôler l'exécution du serveur
    :type flag: list
    :param clients: Liste des clients connectés
    :type clients: list
    """
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
            elif message.startswith("profile:request"):
                # Gérer la demande de profil
                identifiant = dico[conn]
                profile_info = info_profile_database(identifiant)
                # Envoyer les informations de profil au client
                profile_info_json = json.dumps(profile_info)
                conn.send(f"profile:{profile_info_json}".encode())
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

        identifiant = dico.get(conn)
        if identifiant is None:
            # Gérer le cas où la connexion n'est plus dans le dictionnaire
            print("La connexion n'est plus dans le dictionnaire.")
            return
        else:
            query = "UPDATE utilisateurs SET statut = 0 WHERE identifiant = %s"
            values = (identifiant,)
            execute_query(query, values)

    except Exception as e:
        print(f"Une exception s'est produite avec {address} : {e}")
    finally:
        # Fermer la connexion du client
        conn.close()

def server_shell(flag_lock, flag, clients,):  
    """
    Gère le shell du serveur, permettant des commandes pour contrôler le serveur.

    :param flag_lock: Serrure pour assurer la cohérence entre les threads sur le drapeau
    :type flag_lock: threading.Lock
    :param flag: Drapeau pour contrôler l'exécution du serveur
    :type flag: list
    :param clients: Liste des clients connectés
    :type clients: list
    """
  
    if not authenticate_shell():
        return

    while flag[0]:
        commande = input("Pour voir les commandes Entrez 'showcommande' ou entrez la commande que vous souhaiter utiliser: ")
        if commande.lower() == "kill":
            with flag_lock:
                flag[0] = False
            send_user_info_flag.set()
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
        elif commande.lower() == "showban":
            print("Clients bannis :")
            for identifiant in get_banned_clients():
                print(f"- {identifiant}")
        elif commande.lower() == "showkick":
            print("Clients kickés :")
            for identifiant, _ in get_kicked_clients():
                print(f"- {identifiant}")
        elif commande.lower().startswith("unban@"):
            parts = commande.split("@")
            if len(parts) == 2:
                identifiant = parts[1].strip()
                unban(identifiant)
            else:
                print("Commande incorrecte. Utilisez 'unban@identifiant'.")

        elif commande.lower().startswith("unkick@"):
            parts = commande.split("@")
            if len(parts) == 2:
                identifiant = parts[1].strip()
                unkick(identifiant)
            else:
                print("Commande incorrecte. Utilisez 'unkick@identifiant'.")
        elif commande.lower() == "showcommande":
            print("Commandes disponibles :")
            print("(Remplacer identifiant par l'identifiant concerné exemple: commande@xxxx)")
            print("- kill : Arrêter le serveur.")
            print("- showdemande : Afficher les demandes de changement de channel en attente.")
            print("- accept@identifiant : Accepter une demande de changement de channel.")
            print("- refuser@identifiant : Refuser une demande de changement de channel.")
            print("- ban@identifiant : Bannir un client.")
            print("- kick@identifiant : Appliquer une sanction kick (bannir pendant 1h).")
            print("- showban : Afficher la liste des clients bannis.")
            print("- showkick : Afficher la liste des clients kickés.")
            print("- unban@identifiant : Lever le ban d'un client.")
            print("- unkick@identifiant : Lever la sanction kick d'un client.")
            print("- showcommande : Afficher toutes les commandes disponibles.")
        else:
            print("Commande non reconnue. Pour voir les commandes utilisez 'showcommande' .")

if __name__ == '__main__':
    """
    Point d'entrée principal du serveur de chat.

    Ce bloc de code est exécuté lorsque le script est lancé directement.

    - Initialise les paramètres du serveur.
    - Crée les structures de données nécessaires.
    - Démarre le thread pour le shell du serveur.
    - Crée le socket du serveur et écoute les connexions entrantes.
    - Crée un thread pour chaque client connecté.

    :param port: Port sur lequel le serveur écoute les connexions.
    :type port: int
    :param flag: Drapeau pour contrôler l'exécution du serveur.
    :type flag: list
    :param flag_lock: Serrure pour assurer la cohérence entre les threads sur le drapeau.
    :type flag_lock: threading.Lock
    :param clients: Liste des clients connectés.
    :type clients: list
    :param dico3: Dictionnaire pour stocker les relations entre les identifiants des clients et les sujets actuels.
    :type dico3: dict
    :param dico: Dictionnaire pour stocker les relations entre les connexions des clients et leurs identifiants.
    :type dico: dict
    :param dico2: Dictionnaire pour stocker les relations entre les identifiants des clients et leurs connexions.
    :type dico2: dict
    :param demandes_en_attente: Dictionnaire pour stocker les demandes de changement de sujet en attente.
    :type demandes_en_attente: dict
    :param Salons_topic: Liste des sujets disponibles pour les salons de chat.
    :type Salons_topic: list
    :param send_user_info_flag: Drapeau pour indiquer quand envoyer des informations sur les utilisateurs.
    :type send_user_info_flag: threading.Event
    :param server_socket: Socket du serveur pour accepter les connexions.
    :type server_socket: socket.socket
    :param shell_thread: Thread pour gérer le shell du serveur.
    :type shell_thread: threading.Thread
    :param send_user_info_thread: Thread pour envoyer des informations sur les utilisateurs aux clients.
    :type send_user_info_thread: threading.Thread
    """
        
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
    send_user_info_flag = threading.Event()

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print("Serveur en attente de connexions...")

    # Créer un thread pour gérer le shell du serveur
    shell_thread = threading.Thread(target=server_shell, args=(flag_lock, flag, clients,))
    shell_thread.start()

    send_user_info_thread = Thread(target=start_send_user_info, args=(clients, flag_lock))

    try:
        server_socket.settimeout(1.0)  # Définir une temporisation sur le socket

        while flag[0]:
            try:
                conn, address = server_socket.accept()
                print(f"Connexion établie avec {address}")

                # Créer un thread pour gérer la connexion client
                client_thread = threading.Thread(target=handle_client, args=(conn, address, flag_lock, flag, clients))
                client_thread.start()
                
                with flag_lock:
                # Ajouter le client à la liste des clients
                    clients.append((conn, None))

                # Démarrer la thread start_send_user_info si ce n'est pas déjà fait
                if not send_user_info_thread.is_alive():
                    send_user_info_thread = threading.Thread(target=send_user_info, args=(clients, flag_lock))
                    send_user_info_thread.start()


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

        # Attendre que la thread start_send_user_info soit démarrée avant de la rejoindre
        if send_user_info_thread.is_alive():
            send_user_info_thread.join()

        shell_thread.join()  # Attendre que le thread du shell se termine
        server_socket.close()


import socket
import threading

def simulate_client():
    # Cette fonction simule un client se connectant au serveur et envoyant le message "arret"
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 10000))  # Remplacez '127.0.0.1' par l'adresse IP du serveur si nécessaire
    client_socket.send("arret".encode())
    client_socket.close()

def handle_client(conn, address, flag_lock, flag):
    reply = "Bonjour"
    flag2 = True
    global clients


    try:
        while flag2:
            message = conn.recv(1024).decode()
            print(f"J'ai reçu le message de {address}: {message}")

            if message.lower() == "bye":
                print(f"Client {address} a demandé de quitter. Fermeture de la connexion.")
                break
            elif message.lower() == "arret":
                print("Commande d'arrêt reçue. Arrêt du serveur.")
                with flag_lock:
                    flag[0] = False
                    flag2 = False
                    for conn in range(len(clients)):
                        clients[conn].send("arret".encode())
                    simulate_client()
                    
            else:
                conn.send(reply.encode())
                print(f"J'ai envoyé le message à {address}: {reply}")

    except ConnectionResetError:
        print(f"La connexion avec {address} a été réinitialisée par le client.")
    except Exception as e:
        print(f"Une exception s'est produite avec {address}: {e}")


if __name__ == '__main__':
    port = 10000
    flag = [True]  # Utiliser une liste pour que la variable soit mutable et puisse être partagée entre les threads
    flag_lock = threading.Lock()
    client_threads = []  # Liste pour stocker les threads clients
    clients = []

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    print("Serveur en attente de connexions...")
    server_socket.listen(5)

    try:
        while flag[0]:
            conn, address = server_socket.accept()
            print(f"Connexion établie avec {address}")

            # Créer un thread pour gérer la connexion client
            client_thread = threading.Thread(target=handle_client, args=(conn, address, flag_lock, flag))
            client_thread.start()

            # Ajouter le client à la liste des clients
            clients.append(conn)
            client_threads.append(client_thread)

    except KeyboardInterrupt:
        print("\nFermeture du serveur suite à une interruption clavier.")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")
    finally:
        # Attendre que tous les threads clients se terminent avant de fermer le serveur
        for thread in client_threads:
            thread.join()
        server_socket.close()

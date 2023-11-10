import socket
import threading

def handle_client(conn, address, flag_lock):
    reply = "Bonjour"
    flag2 = True

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
                    global flag
                    flag = False
                    flag2 = False
            else:
                conn.send(reply.encode())
                print(f"J'ai envoyé le message à {address}: {reply}")

    except ConnectionResetError:
        print(f"La connexion avec {address} a été réinitialisée par le client.")
    except Exception as e:
        print(f"Une exception s'est produite avec {address}: {e}")

    finally:
        conn.close()
        print(f"La connexion avec {address} a été fermée.")

if __name__ == '__main__':
    port = 10000
    flag = True
    flag_lock = threading.Lock()
    client_threads = []  # Liste pour stocker les threads clients

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    print("Je me connecte")
    server_socket.listen(5)

    try:
        while flag:
            conn, address = server_socket.accept()
            print(f"Connexion établie avec {address}")

            # Créer un thread pour gérer la connexion client
            client_thread = threading.Thread(target=handle_client, args=(conn, address, flag_lock))
            client_thread.start()

            # Ajouter le thread client à la liste
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
  
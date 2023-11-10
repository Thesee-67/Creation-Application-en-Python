import socket

if __name__ == '__main__':
    port = 10000
    reply = "Bonjour"
    flag = True

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    print("Je me connecte")
    server_socket.listen(1)

    try:
        while flag:
            conn, address = server_socket.accept()
            flag2 = True  # Réinitialiser flag2 pour chaque nouvelle connexion

            while flag2:
                try:
                    message = conn.recv(1024).decode()
                    print("J'ai reçu le message", message)

                    if message.lower() == "bye":
                        print("Client a demandé de quitter. Attente de la déconnexion du client...")
                        flag2 = False  # Sortir de la boucle interne
                    elif message.lower() == "arret":
                        print("Commande d'arrêt reçue. Arrêt du serveur.")
                        flag2 = False
                        flag = False
                    else:
                        conn.send(reply.encode())
                        print("J'ai envoyé le message", reply)

                except ConnectionResetError:
                    print("La connexion a été réinitialisée par le client.")
                    flag2 = False  # Sortir de la boucle interne en cas d'erreur
                except Exception as e:
                    print(f"Une exception s'est produite : {e}")
                    flag2 = False  # Sortir de la boucle interne en cas d'erreur

            conn.close()
             # La connexion sera fermée ici après la boucle interne

    except KeyboardInterrupt:
        print("\nFermeture du serveur suite à une interruption clavier.")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")
    finally:
        server_socket.close()

import socket

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10000
    flag = True

    try:
        client_socket = socket.socket()
        client_socket.connect((host, port))

        while flag:
            try:
                message = input("Entrez le message à envoyer (ou 'bye' pour quitter ou 'arret' pour arrêter le serveur): ")

                client_socket.send(message.encode())

                if message.lower() == "bye":
                    print("Demande de déconnexion envoyée au serveur. Fermeture du client.")
                    flag = False
                elif message.lower() == "arret":
                    print("Arrêt du Client et du Serveur")
                    flag = False
                else:
                    reply = client_socket.recv(1024).decode()
                    print("J'ai reçu le message:", reply)

                    # Vérifier si le message du serveur est "arret_serveur"
                    if reply.lower() == "arret_serveur":
                        print("Le serveur a demandé l'arrêt. Fermeture du client.")
                        flag = False

            except (socket.error, socket.timeout) as e:
                print(f"Erreur de socket : {e}")
                break  # Sortir de la boucle en cas d'erreur
            except Exception as e:
                print(f"Une exception s'est produite : {e}")
                break  # Sortir de la boucle en cas d'erreur

    except KeyboardInterrupt:
        print("\nFermeture du client suite à une interruption clavier.")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")
    finally:
        client_socket.close()

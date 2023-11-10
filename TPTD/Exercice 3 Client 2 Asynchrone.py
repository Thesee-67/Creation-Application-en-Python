import socket

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10000
    flag = True

    try:
        try:
            client_socket = socket.socket()
            client_socket.connect((host, port))

            while flag:
                message = input("Entrez le message à envoyer (ou 'bye' pour quitter ou 'arret' pour arreter le serveur): ")
                
                client_socket.send(message.encode())
                
                if message == "bye":
                    print("Demande de déconnexion envoyée au serveur. Fermeture du client.")
                    flag = False
                elif message == "arret":
                    print("Arret du Client et Serveur")
                    flag = False
                else:
                    reply = client_socket.recv(1024).decode()
                    print("J'ai reçu le message", reply)

        except (socket.error, socket.timeout) as e:
            print(f"Erreur de socket : {e}")
        except Exception as e:
            print(f"Une exception s'est produite : {e}")

        finally:
            client_socket.close()

    except KeyboardInterrupt:
        print("\nFermeture du client suite à une interruption clavier.")
    except Exception as e:
        print(f"Une exception s'est produite : {e}")

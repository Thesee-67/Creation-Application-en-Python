import socket
import threading
import time

def rcv(client_socket):
    try:
        reply = ""
        while reply != "bye" and reply != "arret":
            reply = client_socket.recv(1024).decode()
            if not reply:
                break  # La connexion a été fermée par le serveur
            print(f"reply is : {reply}")

        print("Server closed. Closing connection.")
    except ConnectionAbortedError:
        print("La connexion a été fermée par le serveur.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

def main():
    message = ""
    host = '127.0.0.1'
    port = 1002

    client_socket = socket.socket()
    client_socket.connect((host, port))

    rcv_thread = threading.Thread(target=rcv, args=[client_socket])
    rcv_thread.start()

    try:
        while message != "bye" and message != "arret":
            time.sleep(0.3)
            message = input("Entrez le message à envoyer : ")
            client_socket.send(message.encode())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

    rcv_thread.join()

if __name__ == '__main__':
    main()

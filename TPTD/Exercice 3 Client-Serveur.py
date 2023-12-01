import socket
import threading
import time

def rcv(client_socket):
    reply = ""
    while reply!="bye" and reply!="arret":
        reply = client_socket.recv(1024).decode()
        print(f"reply is : {reply}")
        if (reply == "bye") or (reply == "arret"):
            client_socket.send(reply.encode())
    client_socket.close()

def main():
    message = ""
    host = '127.0.0.1'
    port = 1000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    rcv_thread = threading.Thread(target=rcv, args=[client_socket])
    rcv_thread.start()

    try:
        while message!="bye" and message!="arret":
            time.sleep(0.3)
            message = input("Entrez le message à envoyer : ")
            client_socket.send(message.encode())
    except OSError as err:
        print(err)
        print("La connection avec le serveur a été interrompue")

    rcv_thread.join()
    client_socket.close()

if __name__ == '__main__':
    main()
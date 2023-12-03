import socket
import threading

def receive(conn, address, host, port):
    global flag
    global clients
    
    msg = ""
    while msg!="bye" and msg!="arret":
        msg = conn.recv(1024).decode()
        print(f"message from {address} is : {msg}")
        if msg=="bye":
            conn.send(msg.encode())
        if msg=="arret":
            flag = False
            for conn in range(len(clients)):
                for key in clients[conn]:
                    key.send("arret".encode())
            fconn(host, port)

def fconn(host, port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    client_socket.send("arret".encode())
    client_socket.close()

def main():
    global flag
    global clients

    host = '0.0.0.0'
    port = 1002
    flag = True
    clients = []

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)

    while flag == True:
        conn, address = server_socket.accept()
        client_thread = threading.Thread(target=receive, args=[conn, address, host, port])
        clients.append({conn:client_thread})
        client_thread.start()

    for thread in range(len(clients)):
        for key in clients[thread]:
            clients[thread][key].join()
    server_socket.close()

if __name__ == '__main__':
    main()
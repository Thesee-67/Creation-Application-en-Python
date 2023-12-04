import socket
import threading

def receive(conn, address, host, port, server_socket):
    global flag
    global clients

    try:
        msg = ""
        while msg != "bye" and msg != "arret":
            msg = conn.recv(1024).decode()
            print(f"message from {address} is: {msg}")
            if msg == "bye":
                conn.send(msg.encode())
            if msg == "arret":
                flag = False
                server_socket.close()
                conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def fconn(host, port, server_socket):
    client_socket = socket.socket()
    client_socket.connect(("127.0.0.1", 1002))
    client_socket.send("arret".encode())
    client_socket.close()
    server_socket.close()

def main():
    global flag

    host = '0.0.0.0'
    port = 1002
    flag = True

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)

    try:
        while flag:
            conn, address = server_socket.accept()
            if not flag:
                break
            client_thread = threading.Thread(target=receive, args=[conn, address, host, port, server_socket])
            client_thread.start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()

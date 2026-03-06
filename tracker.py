import socket
import threading

peers = []

def handle_client(conn, addr):
    print("Connected:", addr)

    port = conn.recv(1024).decode()
    peer = (addr[0], int(port))

    peers.append(peer)

    conn.send(str(peers).encode())
    conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen()

print("Tracker running on port 5000")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
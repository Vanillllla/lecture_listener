import socket
import os
import struct

HOST = "0.0.0.0"
PORT = 5001
BUFFER = 4096

# Папка "Recordings" рядом со скриптом
save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Recordings")
os.makedirs(save_dir, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Listening on port {PORT}...")

conn, addr = server.accept()
print(f"Connected from {addr}")

# Получаем длину имени файла, затем имя
name_len = struct.unpack("I", conn.recv(4))[0]
filename = conn.recv(name_len).decode()

# Получаем размер файла
file_size = struct.unpack("Q", conn.recv(8))[0]

save_path = os.path.join(save_dir, filename)
received = 0

with open(save_path, "wb") as f:
    while received < file_size:
        data = conn.recv(min(BUFFER, file_size - received))
        if not data:
            break
        f.write(data)
        received += len(data)

print(f"Saved: {save_path} ({received} bytes)")
conn.close()
server.close()

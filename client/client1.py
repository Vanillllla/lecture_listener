import socket
import os
import struct

SERVER_IP = "192.168.1.106"
PORT = 5001
BUFFER = 4096

filepath = r"111.aac"

filename = os.path.basename(filepath)
file_size = os.path.getsize(filepath)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

# Отправляем длину имени файла + имя
name_encoded = filename.encode()
client.send(struct.pack("I", len(name_encoded)))
client.send(name_encoded)

# Отправляем размер файла
client.send(struct.pack("Q", file_size))

# Отправляем содержимое файла
sent = 0
with open(filepath, "rb") as f:
    while chunk := f.read(BUFFER):
        client.sendall(chunk)
        sent += len(chunk)
        print(f"Sent: {sent}/{file_size} bytes", end="\r")

print(f"\nDone! Sent {filename}")

raw = client.recv(4)
text_len = struct.unpack("I", raw)[0]
text = client.recv(text_len).decode("utf-8")
print("Transcription:", text)

client.close()

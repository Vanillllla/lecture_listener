# sender.py
import socket
import os

HOST = "192.168.0.10"   # IP получателя
PORT = 5000
FILENAME = "audio.wav"  # локальный файл для отправки

def main():
    filesize = os.path.getsize(FILENAME)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        header = f"{os.path.basename(FILENAME)}|{filesize}\n"
        s.sendall(header.encode("utf-8"))

        with open(FILENAME, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                s.sendall(chunk)

if __name__ == "__main__":
    main()

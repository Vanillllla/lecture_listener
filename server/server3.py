import socket
import os
import struct
import whisper as wh

HOST = "0.0.0.0"
PORT = 5001
BUFFER = 4096

# Папка для сохранения записей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "Recordings")
os.makedirs(SAVE_DIR, exist_ok=True)

# Загружаем модель Whisper один раз
model = wh.load_model("large")  # или "base", "medium", etc.

def receive_file(conn):
    # 1) длина имени файла (4 байта, unsigned int)
    raw = conn.recv(4)
    if len(raw) < 4:
        raise ConnectionError("Failed to read filename length")
    name_len = struct.unpack("I", raw)[0]

    # 2) имя файла
    filename = conn.recv(name_len).decode("utf-8")

    # 3) размер файла (8 байт, unsigned long long)
    raw = conn.recv(8)
    if len(raw) < 8:
        raise ConnectionError("Failed to read file size")
    file_size = struct.unpack("Q", raw)[0]

    save_path = os.path.join(SAVE_DIR, filename)
    received = 0

    with open(save_path, "wb") as f:
        while received < file_size:
            chunk = conn.recv(min(BUFFER, file_size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print(f"Saved: {save_path} ({received} bytes)")
    return save_path

def transcribe_file(path: str) -> str:
    # language="ru" для русского
    result = model.transcribe(path, language="ru")
    return result.get("text", "").strip()

def send_text(conn, text: str):
    data = text.encode("utf-8")
    conn.sendall(struct.pack("I", len(data)))
    conn.sendall(data)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"Listening on port {PORT}...")

    while True:
        conn, addr = server.accept()
        print(f"Connected from {addr}")
        try:
            audio_path = receive_file(conn)
            text = transcribe_file(audio_path)
            send_text(conn, text)
        except Exception as e:
            print("Error:", e)
            try:
                send_text(conn, f"ERROR: {e}")
            except Exception:
                pass
        finally:
            conn.close()

if __name__ == "__main__":
    main()

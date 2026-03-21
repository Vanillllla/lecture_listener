import socket
import os
import struct
import whisper as wh
from datetime import datetime
from g4f.client import Client

HOST = "0.0.0.0"
PORT = 5001
BUFFER = 4096

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_DIR = os.path.join(BASE_DIR, "Recordings")
TRANS_DIR = os.path.join(BASE_DIR, "transcriptions")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "system_for_ai", "system_prompt.txt")

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(TRANS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Загружаем Whisper
model = wh.load_model("large-v3-turbo")


def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# --- SYSTEM PROMPT ---
def load_system_prompt():
    if not os.path.exists(SYSTEM_PROMPT_PATH):
        raise FileNotFoundError(f"System prompt not found: {SYSTEM_PROMPT_PATH}")
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


# --- RECEIVE FILE ---
def receive_file(conn):
    raw = conn.recv(4)
    if len(raw) < 4:
        raise ConnectionError("Failed to read filename length")
    name_len = struct.unpack("I", raw)[0]

    filename = conn.recv(name_len).decode("utf-8")

    raw = conn.recv(8)
    if len(raw) < 8:
        raise ConnectionError("Failed to read file size")
    file_size = struct.unpack("Q", raw)[0]

    ts = timestamp()
    filename = f"{ts}_{filename}"
    save_path = os.path.join(SAVE_DIR, filename)

    received = 0
    with open(save_path, "wb") as f:
        while received < file_size:
            chunk = conn.recv(min(BUFFER, file_size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print(f"Saved audio: {save_path}")
    return save_path, ts


# --- TRANSCRIBE ---
def transcribe_file(path: str) -> str:
    result = model.transcribe(path, language="ru", fp16=False)
    return result.get("text", "").strip()


def save_transcription(text: str, ts: str):
    filename = f"{ts}_transcription.txt"
    path = os.path.join(TRANS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved transcription: {path}")
    return path


# --- GPT ---
def build_user_prompt(text: str):
    return f"""
Ниже приведена транскрипция лекции.

{text}

Сделай краткий структурированный конспект в LaTeX.
"""


def summarize_with_g4f(text: str) -> str:
    client = Client()
    system_prompt = load_system_prompt()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_prompt(text)}
        ],
        web_search=False
    )

    return response.choices[0].message.content


def save_summary(text: str, ts: str):
    filename = f"{ts}_summary.tex"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved summary: {path}")
    return path


# --- SEND ---
def send_text(conn, text: str):
    data = text.encode("utf-8")
    conn.sendall(struct.pack("I", len(data)))
    conn.sendall(data)


# --- MAIN ---
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Listening on port {PORT}...")

    while True:
        conn, addr = server.accept()
        print(f"Connected from {addr}")

        try:
            audio_path, ts = receive_file(conn)

            # 1. Транскрипция
            text = transcribe_file(audio_path)
            save_transcription(text, ts)

            # 2. Генерация конспекта
            summary = summarize_with_g4f(text)
            save_summary(summary, ts)

            # 3. Отправка клиенту
            send_text(conn, summary)

        except Exception as e:
            print("Error:", e)
            try:
                send_text(conn, f"ERROR: {e}")
            except:
                pass

        finally:
            conn.close()


if __name__ == "__main__":
    main()

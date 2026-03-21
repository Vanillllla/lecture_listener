# receiver.py
import socket
import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel

HOST = "0.0.0.0"
PORT = 5000
MODEL_PATH = "vosk-model-small-ru-0.22"  # папка модели

def transcribe(path):
    SetLogLevel(0)
    wf = wave.open(path, "rb")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
        raise ValueError("Нужен WAV: mono, 16-bit PCM")

    model = Model(model_path=MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    parts = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            parts.append(res.get("text", ""))

    final = json.loads(rec.FinalResult())
    parts.append(final.get("text", ""))

    return " ".join(p for p in parts if p)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Listening on {HOST}:{PORT} ...")

        conn, addr = s.accept()
        with conn:
            print("Connected from", addr)

            header = b""
            while not header.endswith(b"\n"):
                data = conn.recv(1)
                if not data:
                    break
                header += data

            header = header.decode("utf-8").strip()
            filename, filesize = header.split("|")
            filesize = int(filesize)
            print(f"Receiving {filename} ({filesize} bytes)")

            received = 0
            with open(filename, "wb") as f:
                while received < filesize:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)

            print("File received, start transcription...")
            try:
                text = transcribe(filename)
                print("Result text:")
                print(text)
            except Exception as e:
                print("Transcription error:", e)

if __name__ == "__main__":
    main()

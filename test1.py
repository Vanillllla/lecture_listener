import whisper

AUDIO_PATH = "audio.wav"  # сюда свой файл

# один раз скачает модель, потом использует локально
model = whisper.load_model("small")

result = model.transcribe(AUDIO_PATH, language="ru")  # language=None для автоопределения
print(result["text"])

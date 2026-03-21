import whisper as wh

print(wh.available_models())

# model = wh.load_model("small")  # или другую []
# result = model.transcribe(r"Recordings/test_sound.wav", language="ru")
# print(result["text"])
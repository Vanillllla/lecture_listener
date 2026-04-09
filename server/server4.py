import os
from g4f.client import Client  # pip install g4f

INPUT_FILE = "transcriptions/transcription_2026-03-21_16-52-45.txt"
OUTPUT_FILE = "output.txt "   # можешь поменять на .txt

SYSTEM_PROMPT = """
Ты — опытный преподаватель технического университета и профессиональный верстальщик LaTeX.
Твоя задача — по транскрипции живой лекции сделать краткий, структурированный конспект.

Требования:
- Пиши на том же языке, что и исходный текст.
- Структурируй конспект: введение, основные определения, теоремы/формулы, примеры, выводы.
- Используй разметку LaTeX: section, subsection, itemize, enumerate, equation (где уместно).
- Не добавляй выдуманных фактов, используй только информацию из транскрипции.
- Если в речи есть повторы, фразы-паразиты, обрывки — убери их, сохрани только суть.
- В начале файла добавь минимальный преамбулу LaTeX для статьи.
- На выходе верни ТОЛЬКО готовый LaTeX-код конспекта без пояснений.
"""

def read_transcript(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_output(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def build_user_prompt(transcript: str) -> str:
    # Здесь можно добавить дополнительные инструкции, например тему/дату лекции
    return (
        "Ниже приведена транскрипция лекции.\n"
        "Сделай по ней краткий, аккуратный конспект в формате LaTeX.\n\n"
        "=== ТРАНСКРИПЦИЯ НАЧАЛО ===\n"
        f"{transcript}\n"
        "=== ТРАНСКРИПЦИЯ КОНЕЦ ===\n"
    )

def summarize_with_g4f(transcript: str) -> str:
    client = Client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(transcript)},
    ]

    # Можно выбрать другую модель, см. документацию g4f
    response = client.chat.completions.create(
        model="gpt-4",  # или g4f.models.default / локальный через g4f.local
        messages=messages,
        web_search=False  # при необходимости
    )

    return response.choices[0].message.content

def main():
    transcript = read_transcript(INPUT_FILE)
    latex_summary = summarize_with_g4f(transcript)
    write_output(OUTPUT_FILE, latex_summary)
    print(f"Готово! Конспект сохранён в {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

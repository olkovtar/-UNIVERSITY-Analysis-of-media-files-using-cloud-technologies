"""
Завдання до виконання:

Необхідно написати скрипт, який приймає на вхід назву файла і перевіряє чи файл є медіа файлом з використанням Python та бібліотек pydub та mutagen. 
Якщо так, то відобразити інформацію про нього: тривалість в секундах, і метадані якщо наявні. Розглядаєм тільки файли форматів mp3 та wav.
"""

from pydub import AudioSegment
from mutagen import File as MutagenFile
import os

def get_audio_info(file_path):
    """
    Перевіряє чи файл є медіа (mp3 або wav) та виводить тривалість у секундах.
    """
    if not os.path.isfile(file_path):
        print("Файл не існує.")
        return False

    # Перевірка розширення файлу
    if not (file_path.lower().endswith(".mp3") or file_path.lower().endswith(".wav")):
        print("Цей формат не підтримується (тільки mp3 та wav).")
        return False
    
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000  # щоб отримати результат в секундах
        
        print(f"Файл: {file_path}")
        print(f"Формат: {file_path.split('.')[-1].upper()}")
        print(f"Тривалість: {duration:.2f} секунд")
        print(f"Частота дискретизації: {audio.frame_rate} Hz")
        print(f"Канали: {audio.channels}")
        print("=" * 50)
        
        return True
    except Exception as e:
        print(f"Не вдалося прочитати файл як аудіо: {e}")
        return False


def get_audio_metadata(file_path):
    """
    Виводить метадані аудіофайлу, якщо вони є.
    """
    try:
        # Завантаження метаданих
        audio_file = MutagenFile(file_path, easy=True)
        
        if audio_file is None:
            print("Не вдалося завантажити файл для читання метаданих.")
            return
        
        print("\n--- Метадані ---")
        
        # Детальна діагностика
        print(f"Тип файлу: {type(audio_file).__name__}")
        
        if hasattr(audio_file, 'tags'):
            if audio_file.tags is None:
                print("ID3 теги: відсутні (None)")
            elif len(audio_file.tags) == 0:
                print("ID3 теги: порожні")
            else:
                print("ID3 теги знайдено:")
                for key, value in audio_file.tags.items():
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value)
                    else:
                        value_str = str(value)
                    print(f"  {key.capitalize()}: {value_str}")
                return
        else:
            print("Атрибут 'tags' відсутній")
        
        # Отримання технічнічної інформації
        try:
            audio_file_detailed = MutagenFile(file_path, easy=False)
            if hasattr(audio_file_detailed, 'info'):
                info = audio_file_detailed.info
                print(f"\nТехнічна інформація:")
                print(f"  Бітрейт: {getattr(info, 'bitrate', 'невідомо')} kbps")
                print(f"  Тривалість: {getattr(info, 'length', 'невідома'):.2f} сек")
                if hasattr(info, 'mode'):
                    print(f"  Режим: {info.mode}")
        except Exception as e:
            print(f"Не вдалося отримати технічну інформацію: {e}")
                
    except Exception as e:
        print(f"Помилка при читанні метаданих: {e}")


def analyze_audio_file(file_path):
    """
    Головна функція для аналізу аудіофайлу.
    """
    print("=" * 50)
    print("АНАЛІЗ АУДІОФАЙЛУ")
    print("=" * 50)
    
    if get_audio_info(file_path):
        get_audio_metadata(file_path)
    
    print("=" * 50)

if __name__ == "__main__":
    while True:
        filename = input("\nВведіть назву файлу (mp3 або wav) або 'exit'/'q' для виходу: ").strip()
        
        if filename.lower() == 'exit' or filename.lower() == 'q':
            print("Роботу завершено.")
            break
            
        if filename:
            analyze_audio_file(filename)
        else:
            print("Будь ласка, введіть назву файлу.")

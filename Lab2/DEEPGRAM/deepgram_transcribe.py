import boto3
import requests
import json
from datetime import datetime
import os

BUCKET_NAME = ""
FILE_KEY = "" # наприклад lab2/lab_2.mp3
REGION = ""

DEEPGRAM_API_KEY = ""
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

def transcribe_audio_deepgram():
    """
    Транскрибує аудіофайл з S3 використовуючи Deepgram API
    """
    # Ініціалізація S3 клієнта з credentials
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        s3_client = boto3.client(
            's3',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    print(f"Завантаження файлу з S3: {BUCKET_NAME}/{FILE_KEY}")

    try:
        # Завантаження файлу з S3 в пам'ять
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        audio_data = response['Body'].read()

        print(f"Файл завантажено ({len(audio_data)} байт)")
        print("Відправка на транскрипцію в Deepgram...")

        # URL для Deepgram API
        url = "https://api.deepgram.com/v1/listen"

        # Параметри для транскрипції
        params = {
            'model': 'nova-2',
            #'detect_language': 'true', # просто автодетекція мови
            'detect_language': ['uk', 'en'], # автодетекція між двома мовами
            #'language': 'uk', # мова без детекції
            'punctuate': 'true',  # Додавання пунктуації
            'diarize': 'false',  # Розпізнавання різних спікерів
            'smart_format': 'true',  # Розумне форматування
            'utterances': 'true',  # Розбиття на висловлювання
        }

        headers = {
            'Authorization': f'Token {DEEPGRAM_API_KEY}',
            'Content-Type': 'audio/mpeg'
        }

        # Відправка запиту до Deepgram
        deepgram_response = requests.post(
            url,
            params=params,
            headers=headers,
            data=audio_data,
            timeout=300
        )

        # Перевірка статусу відповіді
        if deepgram_response.status_code == 200:
            print("Транскрипція завершена успішно!")

            # Парсинг результату
            result = deepgram_response.json()

            # Збереження повного JSON результату
            json_output = f"transcription_deepgram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"Повний JSON результат збережено: {json_output}")

            # Витягнення тексту транскрипції
            if 'results' in result and 'channels' in result['results']:
                transcript_text = result['results']['channels'][0]['alternatives'][0]['transcript']

                # Збереження чистого тексту (транскрипції)
                text_output = json_output.replace('.json', '.txt')
                with open(text_output, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(transcript_text)

                print(f"\n{'='*60}")
                print("ТРАНСКРИПЦІЯ:")
                print(f"{'='*60}")
                print(transcript_text)
                print(f"{'='*60}\n")
                print(f"Текст транскрипції збережено: {text_output}")

                # Додаткова інформація
                if 'metadata' in result:
                    duration = result['metadata'].get('duration', 'N/A')
                    print(f"\nТривалість аудіо: {duration} секунд")
            else:
                print("Не вдалося витягнути текст з результату")

        else:
            print(f"Помилка Deepgram API: {deepgram_response.status_code}")
            print(f"Відповідь: {deepgram_response.text}")

    except boto3.exceptions.Boto3Error as e:
        print(f"Помилка AWS S3: {str(e)}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Помилка HTTP запиту: {str(e)}")
        raise
    except Exception as e:
        print(f"Помилка: {str(e)}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("DEEPGRAM API - ТРАНСКРИПЦІЯ АУДІО З S3")
    print("="*60)

    # Перевірка креденшиалів
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not BUCKET_NAME or not FILE_KEY or not REGION:
        print("\nУВАГА: AWS credentials не налаштовані!")
        print("Вкажіть AWS_ACCESS_KEY_ID; AWS_SECRET_ACCESS_KEY; BUCKET_NAME; FILE_KEY; REGION у коді")
    elif not DEEPGRAM_API_KEY:
        print("\nУВАГА: DEEPGRAM credentials не налаштовані!")
        print("Вкажіть DEEPGRAM_API_KEY у коді")
    else:
        transcribe_audio_deepgram()

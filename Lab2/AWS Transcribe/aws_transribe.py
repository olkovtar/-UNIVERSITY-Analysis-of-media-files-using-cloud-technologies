import boto3
import time
import json
from datetime import datetime
import os
from urllib.parse import urlparse

BUCKET_NAME = ""
FILE_KEY = "" # наприклад lab2/lab_2.mp3
REGION = ""

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

def transcribe_audio_aws():
    """
    Транскрибує аудіофайл з S3 використовуючи AWS Transcribe
    """
    # Ініціалізація клієнтів AWS з credentials
    if REGION and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        transcribe_client = boto3.client(
            'transcribe',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        s3_client = boto3.client(
            's3',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        return "Заповніть AWS креденшиали в коді"

    # Генерація унікального імені для job
    job_name = f"transcription-job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # URI файлу в S3
    s3_uri = f"s3://{BUCKET_NAME}/{FILE_KEY}"

    print(f"Запуск транскрипції для файлу: {s3_uri}")
    print(f"Ім'я завдання: {job_name}")

    try:
        # Запуск транскрипції
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='mp3',
            IdentifyLanguage=True,
            OutputBucketName=BUCKET_NAME, # зберігаєм результат в бакеті
            OutputKey=f"lab2/completed-transcriptions/{job_name}.json",
            Settings={
                'ShowSpeakerLabels': False
            }
        )

        print("Транскрипція розпочата. Очікування завершення...")

        # Очікування завершення транскрипції
        while True:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']

            if job_status in ['COMPLETED', 'FAILED']:
                break

            print(f"Статус: {job_status}. Очікування 5 секунд...")
            time.sleep(5)

        if job_status == 'COMPLETED':
            print("Транскрипція завершена успішно!")

            # Отримання результатів
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            print(f"URI результату: {transcript_uri}")

            # Завантаження результату з S3
            parsed = urlparse(transcript_uri)
            s3_key = parsed.path.lstrip("/").split("/", 1)[1]

            local_output = f"transcription_aws_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            s3_client.download_file(BUCKET_NAME, s3_key, local_output)
            print(f"Результат збережено в файл: {local_output}")

            # Читання вмісту транскрипції
            with open(local_output, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
                transcript_text = transcript_data['results']['transcripts'][0]['transcript']

                # Збереження чистого тексту (транскрипції)
                text_output = local_output.replace('.json', '.txt')
                with open(text_output, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(transcript_text)

                print(f"\n{'='*60}")
                print("ТРАНСКРИПЦІЯ:")
                print(f"{'='*60}")
                print(transcript_text)
                print(f"{'='*60}\n")
                print(f"Текст транскрипції збережено в файл: {text_output}")

        else:
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Невідома причина')
            print(f"Транскрипція не вдалася: {failure_reason}")

    except Exception as e:
        print(f"Помилка: {str(e)}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("AWS TRANSCRIBE - ТРАНСКРИПЦІЯ АУДІО З S3")
    print("="*60)

    # Перевірка AWS credentials
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not BUCKET_NAME or not FILE_KEY or not REGION:
        print("\nУВАГА: AWS credentials не налаштовані!")
        print("Вкажіть AWS_ACCESS_KEY_ID; AWS_SECRET_ACCESS_KEY; BUCKET_NAME; FILE_KEY; REGION у коді")
    else:       
        transcribe_audio_aws()

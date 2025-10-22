import argparse
import boto3
import time
import json
import os
from datetime import datetime
from urllib.parse import urlparse

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from langdetect import detect
import spacy

# ============== CONFIG ==============
BUCKET_NAME = os.getenv("BUCKET_NAME") or ""
REGION = os.getenv("REGION") or ""

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or ""
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or ""

# Завантаження бібліотек
nltk.download('vader_lexicon', quiet=True)
nlp = spacy.load("en_core_web_sm")


# ============== AWS UPLOAD + TRANSCRIBE ==============
def upload_to_s3(local_path: str, bucket: str, prefix: str = "lab3/input"):
    """Завантажує локальний файл у S3 і повертає його URI"""

    # Перевірка AWS credentials
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, bucket]):
        print("AWS креденшіали або параметри бакету не заповнені!")
        print("Перевірте змінні AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, BUCKET_NAME.")
        return None

    try:
        s3_client = boto3.client(
            's3',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        file_name = os.path.basename(local_path)
        s3_key = f"{prefix}/{file_name}"

        print(f"\nЗавантаження {file_name} до S3...")
        s3_client.upload_file(local_path, bucket, s3_key)
        print(f"Завантажено: s3://{bucket}/{s3_key}")
        return f"s3://{bucket}/{s3_key}"

    except Exception as e:
        print(f"Помилка при завантаженні файлу в S3: {e}")
        return None


def transcribe_audio_aws(file_uri: str):
    """Виконує транскрипцію аудіо через AWS Transcribe"""

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, BUCKET_NAME]):
        print("AWS креденшіали або параметри відсутні! Припинення виконання.")
        return None

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

    job_name = f"transcription-job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"\nЗапуск транскрипції: {job_name}")

    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='wav',
            IdentifyLanguage=True,
            OutputBucketName=BUCKET_NAME,
            OutputKey=f"lab3/completed/{job_name}.json",
            Settings={'ShowSpeakerLabels': False}
        )

        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                break
            print(f"Статус: {job_status} ... очікування 5 с")
            time.sleep(5)

        if job_status == 'FAILED':
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Невідома причина')
            print(f"Transcription failed: {failure_reason}")
            return None

        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        parsed = urlparse(transcript_uri)
        s3_key = parsed.path.lstrip("/").split("/", 1)[1]

        local_output = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        s3_client.download_file(BUCKET_NAME, s3_key, local_output)

        with open(local_output, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["results"]["transcripts"][0]["transcript"]

    except Exception as e:
        print(f"Помилка при транскрипції: {e}")
        return None


# ============== NLP UTILS ==============
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"


def analyze_sentiment(text: str) -> str:
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def search_phrase_and_entities(text: str, phrase: str):
    text_lower = text.lower()
    phrase_lower = phrase.lower()
    position = text_lower.find(phrase_lower)
    phrase_result = "Phrase Not Found" if position == -1 else f"Phrase Found at position: {position}"

    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return phrase_result, entities


# ============== MAIN ==============
def main():
    parser = argparse.ArgumentParser(description="Audio Transcription + NLP Analysis App")
    parser.add_argument("--audio-source", required=True, help="Path to WAV audio file")
    parser.add_argument("--phrase", required=True, help="Phrase to search in the transcribed text")
    args = parser.parse_args()

    # Перевірка AWS credentials перед стартом
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not BUCKET_NAME or not REGION:
        print("\nУВАГА: AWS credentials не налаштовані!")
        print("Вкажіть AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME та REGION у коді або середовищі.")
        return

    # Завантажуємо локальний файл у S3
    s3_uri = upload_to_s3(args.audio_source, BUCKET_NAME)
    if not s3_uri:
        return

    # Транскрипція
    text = transcribe_audio_aws(s3_uri)
    if not text:
        print("Не вдалося отримати транскрипцію.")
        return

    # Мова, сентімент, пошук, NER
    lang = detect_language(text)
    sentiment = analyze_sentiment(text)
    phrase_result, entities = search_phrase_and_entities(text, args.phrase)

    # Вивід
    print("\n" + "=" * 60)
    print("TRANSCRIPTION:")
    print("=" * 60)
    print(text)
    print("=" * 60)
    print(f"Language: {lang}")
    print(f"Sentiment: {sentiment}")
    print(phrase_result)
    print("Named entities:")
    if entities:
        for ent_text, ent_label in entities:
            print(f"  - {ent_text} ({ent_label})")
    else:
        print("  - None")


if __name__ == "__main__":
    main()

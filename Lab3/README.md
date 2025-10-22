Lab 3 — Audio Transcription and NLP Analysis
Цей консольний застосунок виконує транскрипцію аудіофайлу у форматі WAV за допомогою AWS Transcribe,
визначає мову тексту, емоційне забарвлення (sentiment), а також здійснює пошук фрази і розпізнавання іменованих сутностей (NER) через spaCy.

1) Встановлення бібліотек
Перед запуском встановіть необхідні залежності:
bashpip install boto3 nltk langdetect spacy
python -m spacy download en_core_web_sm

2) Налаштування AWS
Для роботи з AWS Transcribe потрібні креденшіали:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- REGION
- BUCKET_NAME

Їх можна:
- Вказати безпосередньо у коді:
pythonAWS_ACCESS_KEY_ID = "YOUR_KEY"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET"
REGION = "eu-north-1"
BUCKET_NAME = "media-analysis-with-aws"
- Або винести у файл .env з такими змінними:
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
REGION=eu-north-1
BUCKET_NAME=media-analysis-with-aws

3) Запуск застосунку
python lab3_app.py --audio-source lab3.wav --phrase "artificial intelligence"

Аргументи:
--audio-source - шлях до локального WAV файлу
--phrase - фраза для пошуку у розпізнаному тексті


Приклад результату
============================================================
TRANSCRIPTION:
============================================================
NASA has launched a new rocket. It was fantastic.
============================================================
Language: en
Sentiment: Positive
Phrase Found at position: 0
Named entities:
  - NASA (ORG)

Примітки
- Локальний файл автоматично завантажується у ваш AWS S3 бакет перед транскрибацією.

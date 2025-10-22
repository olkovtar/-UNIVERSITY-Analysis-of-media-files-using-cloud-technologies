# Lab 3 — Audio Transcription and NLP Analysis

Цей консольний застосунок виконує транскрипцію аудіофайлу у форматі WAV за допомогою AWS Transcribe, визначає мову тексту, його емоційне забарвлення (sentiment), а також здійснює пошук ключової фрази та розпізнавання іменованих сутностей (NER) за допомогою бібліотеки spaCy.

---

## 1. Встановлення бібліотек

Перед першим запуском необхідно встановити усі залежності:

```bash
pip install boto3 nltk langdetect spacy
python -m spacy download en_core_web_sm
```

---

## 2. Налаштування AWS

Для взаємодії з сервісом AWS Transcribe потрібні ваші креденшіали.

- **Необхідні змінні:**
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `REGION`
  - `BUCKET_NAME`

### Спосіб 1: Вказати у коді

Ви можете задати їх як константи безпосередньо у вихідному коді вашого скрипта.

```python
AWS_ACCESS_KEY_ID = "YOUR_KEY"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET"
REGION = "YOUR_AWS_REGION"
BUCKET_NAME = "YOUR_BUCKET_NAME"
```

### Спосіб 2 (рекомендований): Використовувати .env файл

Створіть файл `.env` у кореневій директорії проєкту та додайте змінні у такому форматі:

```dotenv
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
REGION=YOUR_AWS_REGION
BUCKET_NAME=YOUR_BUCKET_NAME
```

---

## 3. Запуск застосунку

Запустіть скрипт з командного рядка, вказавши шлях до аудіофайлу та фразу для пошуку.

```bash
python <lab3_app>.py --audio-source <path_to_wav_audio> --phrase <searched phrase>
```
Наприклад:

```bash
python lab3_app.py --audio-source lab3.wav --phrase "NASA"
```

### Аргументи

- `--audio-source` — шлях до вашого локального WAV файлу.
- `--phrase` — фраза, яку потрібно знайти у розпізнаному тексті.

---

## Приклад результату

```
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
```

---

## Примітки

- Локальний аудіофайл автоматично завантажується у ваш AWS S3 бакет перед початком процесу транскрибації.
- Переконайтеся, що бакет `BUCKET_NAME` існує та у вашого користувача є права на читання/запис.
- Модель `spaCy` використовується англійською (`en_core_web_sm`). Для інших мов підберіть відповідну модель або інструменти аналізу.

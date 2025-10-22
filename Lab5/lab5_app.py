import sys
import json
import cv2
from PIL import Image, ExifTags
import os
import argparse


def is_valid_jpeg(filepath):
    """Перевіряє валідність JPEG-файлу"""
    try:
        with Image.open(filepath) as img:
            img.verify()  # Перевірка на валідність
        return True
    except Exception as e:
        print(f"Файл не є валідним JPEG: {e}")
        return False


def extract_exif_metadata(filepath):
    """Отримує EXIF-метадані з зображення"""
    metadata = {}
    try:
        with Image.open(filepath) as img:
            exif_data = img.getexif()
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    
                    # Декодуємо байтові рядки
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    
                    metadata[tag_name] = value
            else:
                print("Метадані EXIF відсутні.")
    except Exception as e:
        print(f"Не вдалося отримати EXIF: {e}")
    
    return metadata


def detect_faces(input_path, output_path):
    """Виявляє обличчя і зберігає результат з червоними рамками"""
    # Завантаження каскаду Хаара
    haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Читаємо зображення
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError("Не вдалося відкрити зображення. Перевірте шлях до файлу.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Виявлення облич
    faces = haar_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=10,
        minSize=(40, 40)
    )

    print(f"Виявлено облич: {len(faces)}")

    # Малюємо рамки
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imwrite(output_path, image)
    print(f"Збережено результат: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="JPEG validator, EXIF extractor, and face detector")
    parser.add_argument("--image", required=True, help="Шлях до JPEG зображення")
    args = parser.parse_args()

    image_path = args.image

    if not os.path.exists(image_path):
        print("Вказаний файл не існує.")
        sys.exit(1)

    print(f"Обробка зображення: {image_path}")

    # Перевірка валідності JPEG
    if not is_valid_jpeg(image_path):
        sys.exit(1)
    print("JPEG файл валідний.")

    # Отримання EXIF-метаданих
    metadata = extract_exif_metadata(image_path)
    json_path = os.path.splitext(image_path)[0] + "_metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"EXIF метадані збережено: {json_path}")

    # Виявлення облич
    output_img_path = os.path.splitext(image_path)[0] + "_faces.jpg"
    detect_faces(image_path, output_img_path)

    print("\nЗавершено успішно!")


if __name__ == "__main__":
    main()

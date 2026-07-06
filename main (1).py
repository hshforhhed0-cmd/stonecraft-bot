import os
import requests
import schedule
import time
import random
from datetime import datetime

# ============================================================
# НАСТРОЙКИ (берутся из переменных окружения на Railway)
# ============================================================
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "17841414449363132")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

POST_HOUR = 10  # Время публикации (UTC+3 = 07:00 UTC)

# ============================================================
# ТЕМЫ ДЛЯ ПОСТОВ
# ============================================================
TOPICS = [
    "Как использовать AI для составления договоров и документов",
    "5 способов сэкономить время с помощью AI в повседневной жизни",
    "Как AI помогает малому бизнесу конкурировать с крупными компаниями",
    "Голосовые ассистенты vs текстовые AI: что выбрать?",
    "Как AI меняет дизайн интерьеров — примеры и инструменты",
    "Бесплатные AI инструменты которые заменят платные сервисы",
    "Как написать продающий текст с помощью AI за 5 минут",
    "AI для обработки фото — лучшие бесплатные инструменты",
    "Как AI помогает изучать иностранные языки",
    "Топ-5 ошибок при работе с ChatGPT и как их избежать",
    "Как AI помогает планировать бюджет и финансы",
    "AI инструменты для создания презентаций за 10 минут",
    "Как использовать AI для анализа конкурентов",
    "AI для генерации идей — как выйти из творческого тупика",
    "Как AI меняет рынок труда — что нужно знать уже сейчас",
]

# ============================================================
# ГЕНЕРАЦИЯ ТЕКСТА ЧЕРЕЗ GROQ (бесплатно)
# ============================================================
def generate_post_text(topic):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": f"""Напиши пост для Instagram блога об AI технологиях на тему: "{topic}"

Требования:
- Длина: 150-200 слов
- Тон: дружелюбный, простой, без технического жаргона
- Начни с цепляющего первого предложения
- Добавь 3-4 конкретных практических совета
- Заверши призывом к действию (задай вопрос аудитории)
- В конце добавь 5-7 хэштегов на русском и английском
- Пиши как будто объясняешь другу, не как корпоративный блог

Пиши только текст поста, без пояснений."""
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.8
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    return result["choices"][0]["message"]["content"]

# ============================================================
# КАРТИНКА (бесплатные изображения Unsplash)
# ============================================================
def get_image_url():
    keywords = [
        "artificial+intelligence",
        "technology+future",
        "digital+innovation",
        "computer+science",
        "robot+technology"
    ]
    keyword = random.choice(keywords)
    return f"https://source.unsplash.com/1080x1080/?{keyword}"

# ============================================================
# ПУБЛИКАЦИЯ В INSTAGRAM
# ============================================================
def publish_to_instagram(image_url, caption):
    # Шаг 1: Создаём медиа-контейнер
    create_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_USER_ID}/media"
    
    response = requests.post(create_url, data={
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    })
    
    result = response.json()
    
    if "id" not in result:
        print(f"❌ Ошибка создания контейнера: {result}")
        return False
    
    container_id = result["id"]
    print(f"✅ Контейнер создан: {container_id}")
    time.sleep(5)
    
    # Шаг 2: Публикуем
    publish_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_USER_ID}/media_publish"
    
    publish_response = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    })
    
    publish_result = publish_response.json()
    
    if "id" in publish_result:
        print(f"✅ Пост опубликован! ID: {publish_result['id']}")
        return True
    else:
        print(f"❌ Ошибка публикации: {publish_result}")
        return False

# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================
def create_and_publish_post():
    print(f"\n🚀 Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    topic = random.choice(TOPICS)
    print(f"📝 Тема: {topic}")
    
    print("✍️ Генерируем текст...")
    caption = generate_post_text(topic)
    print(f"✅ Текст готов")
    
    image_url = get_image_url()
    print(f"🖼️ Картинка: {image_url}")
    
    print("📤 Публикуем...")
    publish_to_instagram(image_url, caption)

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    print(f"⏰ Бот запущен. Публикация каждый день в {POST_HOUR}:00")
    schedule.every().day.at(f"{POST_HOUR:02d}:00").do(create_and_publish_post)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

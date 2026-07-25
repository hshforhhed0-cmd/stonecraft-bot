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
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "27857289577221820")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

POST_HOUR = 10  # Время публикации (UTC+3 = 07:00 UTC)

# ============================================================
# ТЕМЫ ДЛЯ ПОСТОВ
# ============================================================
TOPICS = [
    "Подоконник из акрилового камня: что это такое и чем он лучше пластика",
    "5 причин заменить старый подоконник на акриловый камень",
    "Как выбрать подоконник — пластик, дерево или акриловый камень",
    "Уход за подоконником из акрилового камня: как сохранить идеальный вид на годы",
    "Бесшовный подоконник — почему это удобно и практично",
    "Какие цвета и текстуры акрилового камня сейчас популярны для подоконников",
    "Ремонт царапин и сколов на акриловом камне своими руками",
    "Чем акриловый камень отличается от пластика и дерева",
    "Подоконник как часть интерьера — современные решения",
    "Сколько стоит подоконник из акрилового камня и от чего зависит цена",
    "Как акриловый камень меняет облик подоконника в квартире",
    "Изготовление подоконника из акрилового камня на заказ — как это происходит",
    "Тёплый подоконник: свойства акрилового камня зимой",
    "Подоконник-столик у окна — тренд в оформлении квартир",
    "Как правильно ухаживать за подоконником, чтобы он служил долго"
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
                "content": f"""Напиши пост для Instagram бренда StoneCraft, который занимается изделиями из акрилового камня (столешницы, подоконники, декоративные панели), на тему: "{topic}"

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
# КАРТИНКА
# ============================================================
def get_image_url():
    return "https://picsum.photos/1080/1080"

# ============================================================
# ПУБЛИКАЦИЯ В INSTAGRAM
# ============================================================
def publish_to_instagram(image_url, caption):
    # Шаг 1: Создаём медиа-контейнер
    create_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_USER_ID}/media"
    
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
    publish_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_USER_ID}/media_publish"
    
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

import json
import requests
from bs4 import BeautifulSoup
import asyncio
import logging
from aiogram import Bot
from config import TELEGRAM_BOT_TOKEN, OWNER_ID, time_stop, depth_key
import datetime


# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
monitoring = False

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# # Инициализация переменной глубины ключа
# depth_key = 5

def load_keywords():
    with open("keywords.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_keywords(keywords):
    with open("keywords.json", "w", encoding="utf-8") as file:
        json.dump([kw.lower() for kw in keywords], file, ensure_ascii=False, indent=4)

def load_groups():
    with open("groups.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_groups(groups):
    with open("groups.json", "w", encoding="utf-8") as file:
        json.dump(groups, file, ensure_ascii=False, indent=4)

def save_additional_data(data):
    with open("add.json", "a", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")

def get_og_data(content):
    soup = BeautifulSoup(content, "html.parser")
    og_title = soup.find("meta", property="og:title")["content"]
    og_description = soup.find("meta", property="og:description")["content"]
    return og_title, og_description

async def monitor(callback, etimer = 0, timer=None):
    global monitoring
    while monitoring:
        groups = load_groups()
        keywords = load_keywords()

        for group in groups:
            etimer += 1
            url = group['url']
            end_key = group['end_key']
            consecutive_matches = group.get('consecutive_matches', 0)  # Инициализируем счетчик совпадений
            now = datetime.datetime.now()
            logging.info(f"Запрос #{etimer} URL: {now.isoformat()} {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                content = response.text

                og_title, og_description = get_og_data(content)
                logging.info(f"og:description для {url}: {og_description}")

                if og_description.lower() == end_key.lower():
                    consecutive_matches += 1
                    logging.info(f"Совпадение {consecutive_matches}/{depth_key} для URL: {url}")
                    if consecutive_matches >= depth_key:
                        parts = url.rstrip('/').rsplit('/', 1)
                        new_num = int(parts[-1]) + 1 - depth_key
                        new_url = f"{parts[0]}/{new_num}"
                        group['url'] = new_url
                        group['consecutive_matches'] = 0  # Сбрасываем счетчик после изменения URL
                        logging.info(f"URL изменен на: {new_url} из-за {depth_key} совпадений подряд")
                    else:
                        group['consecutive_matches'] = consecutive_matches
                else:
                    group['consecutive_matches'] = 0  # Сбрасываем счетчик если описания не совпадают

                    # Проверяем ключевые слова только если og_description не равен end_key
                    found_keywords = [kw for kw in keywords if kw.lower() in og_description.lower()]

                    if found_keywords:
                        timestamp = response.headers.get("Date", "Unknown time")
                        data = {
                            "url": url,
                            "timestamp": timestamp,
                            "og_title": og_title,
                            "og_description": og_description,
                            "found_keywords": found_keywords
                        }
                        save_additional_data(data)

                        message = (
                            f"URL: {url}\n"
                            f"Время: {timestamp}\n"
                            f"Группа: {og_title}\n"
                            f"Запись: {og_description}\n"
                            f"Обнаружено: {', '.join(found_keywords)}"
                        )
                        await callback(message)

                # Обновляем URL на следующий
                parts = url.rstrip('/').rsplit('/', 1)
                new_num = int(parts[-1]) + 1
                if consecutive_matches >= depth_key:
                    new_num = int(parts[-1]) + 1 - depth_key
                    await asyncio.sleep(60)
                new_url = f"{parts[0]}/{new_num}"
                group['url'] = new_url

                # Сохраняем изменения в группе
                save_groups(groups)

            except requests.RequestException as e:
                logging.error(f"Ошибка при запросе {url}: {e}")

        await asyncio.sleep(time_stop)

async def start_monitoring(callback):
    global monitoring
    if not monitoring:
        monitoring = True
        await monitor(callback)

def stop_monitoring():
    global monitoring
    monitoring = False

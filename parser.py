import json
import requests
from bs4 import BeautifulSoup
import asyncio
import logging
from config import (logging_parser,
                    time_stop,
                    depth_key,
                    smoke_break,
                    KEYWORDS_FILE_PATH,
                    EXCEPTIONS_FILE_PATH,
                    GROUPS_FILE_PATH,
                    ADD_FILE_PATH)
import datetime


monitoring = False


# Настройка логирования
logging.basicConfig(level=logging.INFO)


def load_keywords():
    with open(KEYWORDS_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_keywords(keywords):
    with open(KEYWORDS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump([kw.lower() for kw in keywords], file, ensure_ascii=False, indent=4)

def load_exceptions():
    with open(EXCEPTIONS_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_exceptions(keywords):
    with open(EXCEPTIONS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump([kw.lower() for kw in keywords], file, ensure_ascii=False, indent=4)


def load_groups():
    with open(GROUPS_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_groups(groups):
    with open(GROUPS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(groups, file, ensure_ascii=False, indent=4)


def save_additional_data(data):
    with open(ADD_FILE_PATH, "a", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")


def get_og_data(content):
    soup = BeautifulSoup(content, "html.parser")
    og_title = soup.find("meta", property="og:title")["content"]
    og_description = soup.find("meta", property="og:description")["content"]
    return og_title, og_description


def remove_url_numbers(url: str) -> str:
    # Удаления цифр в конце URL
    # return re.sub(r'/\d+$', '', url)
    return f"{url.rstrip('/').rsplit('/', 1)[0]}/"


async def monitor(callback, etimer=0, timer=None):
    global monitoring
    while monitoring:
        groups = load_groups()
        keywords = load_keywords()
        exceptions = load_exceptions()

        for group in groups:
            etimer += 1
            url = group["url"]
            end_key = group["end_key"]
            consecutive_matches = group.get(
                "consecutive_matches", 0
            )  # Инициализируем счетчик совпадений
            now = datetime.datetime.now()
            if logging_parser:
                logging.info(f"Запрос #{etimer} URL: {now.isoformat()} {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                content = response.text

                og_title, og_description = get_og_data(content)
                if logging_parser:
                    logging.info(f"og:description для {url}: {og_description}")

                if og_description.lower() == end_key.lower():
                    consecutive_matches += 1
                    if logging_parser:
                        logging.info(
                            f"Совпадение {consecutive_matches}/{depth_key} для URL: {url}"
                        )
                    if consecutive_matches >= depth_key:
                        parts = url.rstrip("/").rsplit("/", 1)
                        new_num = int(parts[-1]) + 1 - depth_key
                        new_url = f"{parts[0]}/{new_num}"
                        group["url"] = new_url
                        group["consecutive_matches"] = (
                            0  # Сбрасываем счетчик после изменения URL
                        )
                        if logging_parser:
                            logging.info(
                                f"URL изменен на: {new_url} из-за {depth_key} совпадений подряд"
                            )
                    else:
                        group["consecutive_matches"] = consecutive_matches
                else:
                    group["consecutive_matches"] = (
                        0  # Сбрасываем счетчик если описания не совпадают
                    )

                    # Проверяем ключевые слова только если og_description не равен end_key
                    found_keywords = [
                        kw for kw in keywords if kw.lower() in og_description.lower()
                    ]

                    if found_keywords:
                        found_exceptions = [
                            ex for ex in exceptions if ex.lower() in og_description.lower()
                        ]
                        # timestamp = response.headers.get("Date", "Unknown time")
                        # data = {
                        #     "found_keywords": found_keywords,
                        #     "found_exceptions": found_exceptions,
                        #     "url": url,
                        #     "og_title": og_title,
                        #     "timestamp": timestamp,
                        #     "og_description": og_description
                        # }
                        # save_additional_data(data)

                        if not found_exceptions:
                            message = (
                                f"<b>Обнаружено:</b> {', '.join(found_keywords)}\n"
                                f'<a href="{url}">{og_title}</a>\n'
                                f"<b>Запись:</b>\n{og_description}\n"
                            )
                            await callback(message)

                # Обновляем URL на следующий
                parts = url.rstrip("/").rsplit("/", 1)
                new_num = int(parts[-1]) + 1
                if consecutive_matches >= depth_key:
                    new_num = int(parts[-1]) + 1 - depth_key
                    await asyncio.sleep(smoke_break)
                new_url = f"{parts[0]}/{new_num}"
                group["url"] = new_url

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


def check_monitoring():
    global monitoring
    if monitoring:
        return "Ведется активное слежение"
    else:
        return "Слежение отключено"

from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USERS_FILE_PATH = "data/users.json"
GROUPS_FILE_PATH = "data/groups.json"
KEYWORDS_FILE_PATH = "data/keywords.json"
ADD_FILE_PATH = "data/add.json"

logging_parser = True # подробные логи парсинга

# временной цикл мониторинга групп:
# максимальная длительность = time_stop * depth_key + smoke_break
time_stop = 1  # темп (пауза между запросами при парсинге)
depth_key = 50  # запросов (возможное количество скрытых сообщений в группе подряд)
smoke_break = 60  # пауза между группами запросов при парсинге (если не найдено новых сообщений)


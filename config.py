from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USERS_FILE_PATH = "users.json"

time_stop = 1 #задержка между запросами при парсинге
depth_key = 50 #возможное количество скрытых сообщений в группе подряд
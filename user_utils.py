import json
import logging
from config import USERS_FILE_PATH

def load_users():
    try:
        with open(USERS_FILE_PATH, "r") as f:
            users = json.load(f).get("users", [])
            # logging.info(f"Loaded users: {users}")
            return users
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading users: {e}")
        return []

def save_users(users):
    try:
        with open(USERS_FILE_PATH, "w") as f:
            json.dump({"users": users}, f)
            logging.info(f"Saved users: {users}")
    except Exception as e:
        logging.error(f"Error saving users: {e}")

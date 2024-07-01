import json
import logging

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f).get("users", [])
            logging.info(f"Loaded users: {users}")
            return users
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading users: {e}")
        return []

def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump({"users": users}, f)
            logging.info(f"Saved users: {users}")
    except Exception as e:
        logging.error(f"Error saving users: {e}")

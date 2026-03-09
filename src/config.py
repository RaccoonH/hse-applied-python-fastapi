import os

from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("DB_FILE")
SECRET = os.getenv("SECRET")
REDIS_ADDRESS = os.getenv("REDIS_ADDRESS")

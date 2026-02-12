import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MICROPHONE_INDEX = None
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
RECORD_TIMEOUT = 1.0
PHRASE_TIMEOUT = 3.0

RECORDINGS_DIR = "recordings"
OUTPUT_DIR = "output"


import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
# load_dotenv(dotenv_path="/var/www/shakarim-admission-bot/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


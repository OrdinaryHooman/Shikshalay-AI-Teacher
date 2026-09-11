import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("GOOGLE_API_KEY", "").strip()

if not api_key:
    print("ERROR: GOOGLE_API_KEY is missing.")
    raise SystemExit(1)

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello and confirm you are working in one short sentence.",
    )
    print("SUCCESS!")
    print(response.text)
except Exception as error:
    print("ERROR:", error)
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY .env dosyasında bulunamadı.")

client = genai.Client(api_key=API_KEY)

models_to_try = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
]

print("Model uyumluluk testi:")
for m in models_to_try:
    try:
        r = client.models.generate_content(model=m, contents="Merhaba")
        print(f"[OK]   {m}  -->  {r.text[:50]}")
    except Exception as e:
        print(f"[FAIL] {m}  -->  {str(e)[:100]}")

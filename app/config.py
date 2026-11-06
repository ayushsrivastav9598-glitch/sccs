import os
import shutil

# If running in Vercel Serverless environment, use /tmp which is the only writable directory
if os.getenv("VERCEL"):
    DATABASE_PATH = "/tmp/campus.db"
    if not os.path.exists(DATABASE_PATH) and os.path.exists("campus.db"):
        shutil.copyfile("campus.db", DATABASE_PATH)
else:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "campus.db")

SECRET_KEY = os.getenv("SECRET_KEY", "ddugu-iet-smart-campus-secret-key-2026")
ALGORITHM = "HS256"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


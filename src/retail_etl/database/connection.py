import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "retail_admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "retail_secure_pass_2026")
DB_NAME = os.getenv("POSTGRES_DB", "moroccan_retail_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
# تعيين البورت 5433 كافتراضي
DB_PORT = os.getenv("POSTGRES_PORT", "5433")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_engine():
    """إنشاء ومشاركة محرك الاتصال بقاعدة البيانات"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        return engine
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        raise e
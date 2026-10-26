import os
import sys
import hashlib
from datetime import datetime
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.retail_etl.database.connection import get_db_engine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def calculate_file_hash(file_path):
    """حساب هاش MD5 للتحقق من عدم تكرار قراءة الملفات"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ingest_raw_sales(batch_id):
    engine = get_db_engine()
    sales_file = os.path.join(DATA_DIR, "sales_2026-10-10.csv")

    if not os.path.exists(sales_file):
        print(f"❌ File not found: {sales_file}")
        return

    file_name = os.path.basename(sales_file)
    file_hash = calculate_file_hash(sales_file)

    with engine.begin() as conn:
        # 1. تسجيل إبتداء الدفعة
        conn.execute(
            text("""
                INSERT INTO ops.etl_batch (batch_id, pipeline_name, status)
                VALUES (:batch_id, 'raw_sales_ingestion', 'RUNNING')
                ON CONFLICT (batch_id) DO NOTHING;
            """),
            {"batch_id": batch_id}
        )

        # 2. قراءة الملف كنصوص خام بدون أي تحويل
        df = pd.read_csv(sales_file, dtype=str)
        record_count = len(df)

        # إعداد أعمدة التتبع الخاصة بـ RAW
        df['batch_id'] = batch_id
        df['file_name'] = file_name

        # 3. تحميل البيانات الخالصة إلى جدول raw.raw_sales
        df.to_sql('raw_sales', con=conn, schema='raw', if_exists='append', index=False)

        # 4. تسجيل البيان في المانيفست ops.etl_file_manifest
        conn.execute(
            text("""
                INSERT INTO ops.etl_file_manifest (batch_id, file_name, file_hash, record_count, status)
                VALUES (:batch_id, :file_name, :file_hash, :record_count, 'SUCCESS');
            """),
            {
                "batch_id": batch_id,
                "file_name": file_name,
                "file_hash": file_hash,
                "record_count": record_count
            }
        )

        # 5. تحديث حالة الدفعة إلى SUCCESS
        conn.execute(
            text("""
                UPDATE ops.etl_batch
                SET status = 'SUCCESS', end_time = CURRENT_TIMESTAMP
                WHERE batch_id = :batch_id;
            """),
            {"batch_id": batch_id}
        )

    print(f"✅ Successful Ingestion of {record_count} raw records from {file_name} under Batch ID: {batch_id}")

if __name__ == "__main__":
    current_batch = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"🚀 Starting Raw Ingestion with Batch ID: {current_batch}")
    ingest_raw_sales(current_batch)
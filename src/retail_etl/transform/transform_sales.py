import os
import sys
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.retail_etl.database.connection import get_db_engine

def parse_date_robust(date_str):
    if pd.isna(date_str) or not date_str or str(date_str).strip() == 'None':
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            pass
    return None

def process_and_transform_sales(batch_id):
    engine = get_db_engine()

    # 1. جلب القوائم المرجعية المتاحة للمتاجر والمنتجات
    with engine.connect() as conn:
        valid_stores = set(r[0] for r in conn.execute(text("SELECT store_id FROM analytics.dim_store")).fetchall())
        valid_products = set(r[0] for r in conn.execute(text("SELECT product_id FROM analytics.dim_product")).fetchall())
        
        # قراءة المبيعات الخام الخاصة بالدفعة الحالية
        raw_df = pd.read_sql(
            text("SELECT * FROM raw.raw_sales WHERE batch_id = :batch_id"),
            conn,
            params={"batch_id": batch_id}
        )

    if raw_df.empty:
        print(f"⚠️ No raw sales records found for batch: {batch_id}")
        return

    accepted_records = []
    rejected_records = []
    seen_sale_ids = set()

    for _, row in raw_df.iterrows():
        payload = row.to_dict()
        rejection_reasons = []

        sale_id = str(row['sale_id']).strip() if pd.notna(row['sale_id']) else None
        store_id = str(row['store_id']).strip() if pd.notna(row['store_id']) else None
        product_id = str(row['product_id']).strip() if pd.notna(row['product_id']) else None

        # أ) فحص معرف الصفقات والتكرار
        if not sale_id or sale_id == 'None':
            rejection_reasons.append("Missing sale_id")
        elif sale_id in seen_sale_ids:
            rejection_reasons.append(f"Duplicate sale_id '{sale_id}' within batch")
        else:
            seen_sale_ids.add(sale_id)

        # ب) فحص المتاجر والمنتجات
        if not store_id or store_id not in valid_stores:
            rejection_reasons.append(f"Invalid or unknown store_id '{store_id}'")
        
        if not product_id or product_id not in valid_products:
            rejection_reasons.append(f"Invalid or unknown product_id '{product_id}'")

        # ج) فحص التاريخ
        parsed_date = parse_date_robust(row['sale_date'])
        if not parsed_date:
            rejection_reasons.append(f"Invalid or missing date '{row['sale_date']}'")

        # د) فحص ومعالجة السعر الفردي
        raw_price = str(row['unit_price']).replace(',', '.').strip() if pd.notna(row['unit_price']) else ""
        try:
            unit_price = float(raw_price)
            if unit_price < 0:
                rejection_reasons.append("Negative unit_price")
        except ValueError:
            rejection_reasons.append(f"Invalid price format '{row['unit_price']}'")
            unit_price = None

        # هـ) فحص الكمية
        try:
            quantity = int(row['quantity'])
            if quantity <= 0:
                rejection_reasons.append(f"Non-positive quantity '{quantity}'")
        except (ValueError, TypeError):
            rejection_reasons.append(f"Invalid quantity format '{row['quantity']}'")
            quantity = None

        # اتخاذ القرار
        if rejection_reasons:
            rejected_records.append({
                "batch_id": batch_id,
                "source_file": str(row['file_name']),
                "record_payload": json.dumps(payload, default=str),
                "rejection_reason": "; ".join(rejection_reasons)
            })
        else:
            accepted_records.append({
                "sale_id": sale_id,
                "batch_id": batch_id,
                "sale_date": parsed_date,
                "store_id": store_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(quantity * unit_price, 2)
            })

    # 4. مسح البيانات القديمة لضمان Idempotency وإدراج البيانات الحديثة
    with engine.begin() as conn:
        # أ) تنظيف السجلات المرفوضة والمقبولة السابقة لنفس الـ batch_id
        conn.execute(text("DELETE FROM ops.etl_rejected_record WHERE batch_id = :batch_id"), {"batch_id": batch_id})
        conn.execute(text("DELETE FROM analytics.fact_sales WHERE batch_id = :batch_id"), {"batch_id": batch_id})

        # ب) إدراج المرفوضات الجديدة
        for rej in rejected_records:
            conn.execute(
                text("""
                    INSERT INTO ops.etl_rejected_record (batch_id, source_file, record_payload, rejection_reason)
                    VALUES (:batch_id, :source_file, :record_payload, :rejection_reason);
                """),
                rej
            )

        # ج) إدراج المقبولات الجديدة
        for acc in accepted_records:
            conn.execute(
                text("""
                    INSERT INTO analytics.fact_sales (sale_id, batch_id, sale_date, store_id, product_id, quantity, unit_price, total_amount)
                    VALUES (:sale_id, :batch_id, :sale_date, :store_id, :product_id, :quantity, :unit_price, :total_amount);
                """),
                acc
            )

    print(f"📊 Transformation Finished for Batch {batch_id}:")
    print(f"   ✅ Accepted Records Inserted into Fact: {len(accepted_records)}")
    print(f"   ❌ Rejected Records Quarantined: {len(rejected_records)}")

if __name__ == "__main__":
    engine = get_db_engine()
    with engine.connect() as conn:
        latest_batch = conn.execute(text("SELECT batch_id FROM ops.etl_batch ORDER BY start_time DESC LIMIT 1")).scalar()

    if latest_batch:
        print(f"🚀 Running Seed & Transformation for Batch: {latest_batch}")
        from src.retail_etl.transform.seed_dimensions import seed_dimensions
        seed_dimensions()
        process_and_transform_sales(latest_batch)
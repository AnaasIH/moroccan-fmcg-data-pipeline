import os
import sys
from datetime import datetime
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.retail_etl.database.connection import get_db_engine
from src.retail_etl.extract.raw_ingestion import ingest_raw_sales
from src.retail_etl.transform.seed_dimensions import seed_dimensions
from src.retail_etl.transform.transform_sales import process_and_transform_sales

def run_end_to_end_pipeline():
    batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print("\n" + "="*60)
    print(f"🚀 STARTING MOROCCAN RETAIL ETL PIPELINE | BATCH: {batch_id}")
    print("="*60)

    try:
        # Step 1: Raw Ingestion
        print("\n▶️ STEP 1: Ingesting Raw Source Files...")
        ingest_raw_sales(batch_id)

        # Step 2: Seed Dimensions
        print("\n▶️ STEP 2: Seeding Master Dimensions...")
        seed_dimensions()

        # Step 3: Transformation & Data Quality Validation
        print("\n▶️ STEP 3: Transforming Sales & Applying Quality Rules...")
        process_and_transform_sales(batch_id)

        # Step 4: Summary Report
        engine = get_db_engine()
        with engine.connect() as conn:
            fact_count = conn.execute(
                text("SELECT COUNT(*) FROM analytics.fact_sales WHERE batch_id = :batch_id"),
                {"batch_id": batch_id}
            ).scalar()
            rejected_count = conn.execute(
                text("SELECT COUNT(*) FROM ops.etl_rejected_record WHERE batch_id = :batch_id"),
                {"batch_id": batch_id}
            ).scalar()

        print("\n" + "="*60)
        print(f"🎉 PIPELINE EXECUTION COMPLETE FOR {batch_id}")
        print(f"   📊 Fact Sales Records Loaded: {fact_count}")
        print(f"   ⚠️ Quarantine Rejected Records: {rejected_count}")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ PIPELINE FAILED FOR BATCH {batch_id}: {str(e)}")

if __name__ == "__main__":
    run_end_to_end_pipeline()
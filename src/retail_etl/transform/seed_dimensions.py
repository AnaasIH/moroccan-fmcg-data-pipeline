import os
import sys
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.retail_etl.database.connection import get_db_engine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def seed_dimensions():
    engine = get_db_engine()
    
    # 1. Seed Stores
    stores_path = os.path.join(DATA_DIR, "stores.csv")
    if os.path.exists(stores_path):
        df_stores = pd.read_csv(stores_path)
        with engine.begin() as conn:
            for _, row in df_stores.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO analytics.dim_store (store_id, store_name, city, region)
                        VALUES (:store_id, :store_name, :city, :region)
                        ON CONFLICT (store_id) DO NOTHING;
                    """),
                    {
                        "store_id": row["store_id"],
                        "store_name": row["store_name"],
                        "city": row["city"],
                        "region": row["region"]
                    }
                )
        print("✅ dim_store seeded successfully.")

    # 2. Seed Products
    products_path = os.path.join(DATA_DIR, "products.xlsx")
    if os.path.exists(products_path):
        df_products = pd.read_excel(products_path)
        with engine.begin() as conn:
            for _, row in df_products.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO analytics.dim_product (product_id, product_name, category, unit_price_mad)
                        VALUES (:product_id, :product_name, :category, :unit_price_mad)
                        ON CONFLICT (product_id) DO NOTHING;
                    """),
                    {
                        "product_id": row["product_id"],
                        "product_name": row["product_name"],
                        "category": row["category"],
                        "unit_price_mad": float(row["unit_price_mad"])
                    }
                )
        print("✅ dim_product seeded successfully.")

if __name__ == "__main__":
    seed_dimensions()
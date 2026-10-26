import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/raw")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_mock_data():
    print("🚀 Generating synthetic source data with realistic data quality issues...")

    # 1. STORES DATA (stores.csv)
    stores_data = {
        "store_id": ["STR_CAS_01", "STR_RAB_01", "STR_MAR_01", "STR_FEZ_01", "STR_TNG_01"],
        "store_name": ["Marjane Anfa", "Carrefour Agdal", "Gueliz Hyper", "Fez Mall Store", "Tanger City Center"],
        "city": ["Casablanca", "Rabat", "Marrakech", "Fes", "Tangier"],
        "region": ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi", "Fès-Meknès", "Tanger-Tétouan-Al Hoceïma"]
    }
    df_stores = pd.DataFrame(stores_data)
    df_stores.to_csv(os.path.join(DATA_DIR, "stores.csv"), index=False)
    print("✅ Created: stores.csv")

    # 2. PRODUCTS DATA (products.xlsx)
    products_data = {
        "product_id": ["PRD_001", "PRD_002", "PRD_003", "PRD_004", "PRD_005", "PRD_006"],
        "product_name": ["Atay Sultan 200g", "Huile Lesieur 5L", "Lait Jaouda 1L", "Couscous Dari 1kg", "Farine MayMouna 5kg", "Jus Valencia 1L"],
        "category": ["Beverages", "Oils & Fats", "Dairy", "Grains", "Grains", "Beverages"],
        "unit_price_mad": [18.50, 95.00, 7.50, 14.00, 45.00, 12.00]
    }
    df_products = pd.DataFrame(products_data)
    df_products.to_excel(os.path.join(DATA_DIR, "products.xlsx"), index=False)
    print("✅ Created: products.xlsx")

    # 3. STOCK DATA (stock.csv)
    stock_data = {
        "snapshot_date": ["2026-10-10"] * 6,
        "store_id": ["STR_CAS_01", "STR_CAS_01", "STR_RAB_01", "STR_RAB_01", "STR_MAR_01", "STR_UNK_99"],
        "product_id": ["PRD_001", "PRD_002", "PRD_001", "PRD_003", "PRD_004", "PRD_005"],
        "quantity_on_hand": [150, -5, 80, 200, 0, 50]  # Intentionally includes negative stock & unknown store
    }
    df_stock = pd.DataFrame(stock_data)
    df_stock.to_csv(os.path.join(DATA_DIR, "stock.csv"), index=False)
    print("✅ Created: stock.csv")

    # 4. SALES DATA (sales_2026-10-10.csv) - WITH QUALITY ISSUES
    sales_data = {
        "sale_id": ["TXN_1001", "TXN_1002", "TXN_1003", "TXN_1004", "TXN_1005", "TXN_1005", "TXN_1006", "TXN_1007", "TXN_1008"],
        "sale_date": ["2026-10-10", "10/10/2026", "2026/10/10", "2026-10-10", "2026-10-10", "2026-10-10", "2026-10-10", None, "2026-10-10"],
        "store_id": ["STR_CAS_01", "STR_RAB_01", "STR_MAR_01", "STR_CAS_01", "STR_FEZ_01", "STR_FEZ_01", "STR_INVALID", "STR_TNG_01", "STR_CAS_01"],
        "product_id": ["PRD_001", "PRD_002", "PRD_003", "PRD_999", "PRD_005", "PRD_005", "PRD_001", "PRD_004", None],
        "quantity": [2, 1, -3, 5, 2, 2, 1, 4, 1],  # Negative quantity & invalid product/store
        "unit_price": ["18.50", "95,00", "7.50", "10.00", "45.00", "45.00", "18.50", "14.00", "18.50"]  # Mixed comma/dot decimals
    }
    df_sales = pd.DataFrame(sales_data)
    df_sales.to_csv(os.path.join(DATA_DIR, "sales_2026-10-10.csv"), index=False)
    print("✅ Created: sales_2026-10-10.csv")

    print("\n🎉 Synthetic dataset successfully generated in data/raw/")

if __name__ == "__main__":
    generate_mock_data()
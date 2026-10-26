import os
import sys
import pandas as pd

# تحديد المسار المطلق لمجلد data/raw
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def profile_dataset(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    print("\n" + "="*60)
    print(f"📄 PROFILING FILE: {file_name}")
    print("="*60)
    
    try:
        # 1. قراءة الملف حسب الصيغة
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            print(f"⚠️ Formato no soportado / Unsupported format: {file_name}")
            return

        # 2. أبعاد الملف والأنواع
        print(f"📊 Dimensions: {df.shape[0]} rows | {df.shape[1]} columns")
        print("\n🔹 Columns & Inferred Data Types:")
        print(df.dtypes)
        
        # 3. القيم المفقودة والتكرارات
        print("\n🔹 Missing Values (Nulls):")
        null_counts = df.isnull().sum()
        print(null_counts[null_counts > 0] if null_counts.sum() > 0 else "None")
        
        print(f"\n🔹 Exact Duplicate Rows: {df.duplicated().sum()}")

        # 4. معايشة وملاحظات خاصة بكل ملف
        print("\n🔹 Sample Data (First 5 Rows):")
        print(df.head(5))

        # 5. كشف المشاكل التخصصية (Specific Quality Checks)
        print("\n🔍 Specific Data Quality Warnings:")
        warnings_found = False

        # فحص الفواصل العشرية والتواريخ في ملف المبيعات
        if "sales" in file_name:
            if "unit_price" in df.columns:
                comma_prices = df['unit_price'].astype(str).str.contains(',').sum()
                if comma_prices > 0:
                    print(f"  ⚠️ [Format Alert] {comma_prices} rows have prices using comma ',' decimal separator.")
                    warnings_found = True
            if "quantity" in df.columns:
                negative_qty = (pd.to_numeric(df['quantity'], errors='coerce') < 0).sum()
                if negative_qty > 0:
                    print(f"  ⚠️ [Business Logic Alert] {negative_qty} rows have negative quantities.")
                    warnings_found = True
            if "sale_id" in df.columns:
                dup_ids = df['sale_id'].duplicated().sum()
                if dup_ids > 0:
                    print(f"  ⚠️ [Integrity Alert] {dup_ids} duplicate sale_id values found.")
                    warnings_found = True

        # فحص الكميات السلبية في المخزون
        if "stock" in file_name and "quantity_on_hand" in df.columns:
            neg_stock = (df['quantity_on_hand'] < 0).sum()
            if neg_stock > 0:
                print(f"  ⚠️ [Business Logic Alert] {neg_stock} rows have negative stock quantities.")
                warnings_found = True

        if not warnings_found:
            print("  ✅ No immediate automated alerts triggered for this file format.")

    except Exception as e:
        print(f"❌ Error inspecting file {file_name}: {str(e)}")

def run_profiling():
    print(f"🔍 Looking for files in: {DATA_DIR}")
    if not os.path.exists(DATA_DIR):
        print(f"❌ Target directory does not exist: {DATA_DIR}")
        return

    files = [f for f in os.listdir(DATA_DIR) if not f.startswith('.')]
    if not files:
        print(f"⚠️ No source files found in {DATA_DIR}.")
        return

    print(f"Found {len(files)} file(s) to analyze: {files}")
    for file in files:
        profile_dataset(file)

if __name__ == "__main__":
    run_profiling()
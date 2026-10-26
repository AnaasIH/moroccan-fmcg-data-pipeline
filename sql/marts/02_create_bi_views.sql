-- 1. View: Daily Sales by Store & City (المبيعات اليومية حسب المتجر والمدينة)
CREATE OR REPLACE VIEW analytics.vw_daily_sales_by_store AS
SELECT
    f.sale_date,
    s.store_name,
    s.city,
    s.region,
    COUNT(f.sales_sk) AS total_transactions,
    SUM(f.quantity) AS total_units_sold,
    SUM(f.total_amount) AS total_revenue_mad
FROM analytics.fact_sales f
JOIN analytics.dim_store s ON f.store_id = s.store_id
GROUP BY f.sale_date, s.store_name, s.city, s.region;

-- 2. View: Revenue by Product Category (الإيرادات حسب فئة المنتج)
CREATE OR REPLACE VIEW analytics.vw_sales_by_category AS
SELECT
    p.category,
    p.product_name,
    SUM(f.quantity) AS total_quantity_sold,
    SUM(f.total_amount) AS total_revenue_mad
FROM analytics.fact_sales f
JOIN analytics.dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.product_name;

-- 3. View: Data Quality & Rejection Analysis (تقرير جودة البيانات للمحللين)
CREATE OR REPLACE VIEW ops.vw_rejection_summary AS
SELECT
    batch_id,
    source_file,
    rejection_reason,
    COUNT(*) AS rejected_records_count,
    MAX(rejected_at) AS last_rejection_time
FROM ops.etl_rejected_record
GROUP BY batch_id, source_file, rejection_reason;
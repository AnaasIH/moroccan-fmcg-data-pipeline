-- 1. Create Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 2. OPS SCHEMA: Operational Audit & Rejection Quarantine
CREATE TABLE IF NOT EXISTS ops.etl_batch (
    batch_id VARCHAR(50) PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS ops.etl_file_manifest (
    manifest_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES ops.etl_batch(batch_id),
    file_name VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64),
    record_count INT,
    status VARCHAR(20) NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ops.etl_rejected_record (
    rejection_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES ops.etl_batch(batch_id),
    source_file VARCHAR(255) NOT NULL,
    record_payload TEXT NOT NULL,
    rejection_reason TEXT NOT NULL,
    rejected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. RAW SCHEMA: Storing source payloads as text
CREATE TABLE IF NOT EXISTS raw.raw_sales (
    raw_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    file_name VARCHAR(255),
    sale_id TEXT,
    sale_date TEXT,
    store_id TEXT,
    product_id TEXT,
    quantity TEXT,
    unit_price TEXT,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. ANALYTICS SCHEMA: Star Schema Dimensions & Facts
CREATE TABLE IF NOT EXISTS analytics.dim_store (
    store_sk SERIAL PRIMARY KEY,
    store_id VARCHAR(50) UNIQUE NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_sk SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price_mad NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    sales_sk SERIAL PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL,
    batch_id VARCHAR(50) REFERENCES ops.etl_batch(batch_id),
    sale_date DATE NOT NULL,
    store_id VARCHAR(50) REFERENCES analytics.dim_store(store_id),
    product_id VARCHAR(50) REFERENCES analytics.dim_product(product_id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.fact_inventory_snapshot (
    snapshot_sk SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    store_id VARCHAR(50) REFERENCES analytics.dim_store(store_id),
    product_id VARCHAR(50) REFERENCES analytics.dim_product(product_id),
    quantity_on_hand INT NOT NULL,
    batch_id VARCHAR(50) REFERENCES ops.etl_batch(batch_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
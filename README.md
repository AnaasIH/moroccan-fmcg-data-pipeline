# 📦 Moroccan FMCG & Supply Chain ETL Data Pipeline

![Data Engineering](https://img.shields.io/badge/Domain-Data_Engineering-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-2.7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Containers-blue.svg)
![Power BI](https://img.shields.io/badge/Power_BI-Analytics-yellow.svg)

## 📌 Executive Summary
A production-grade, fully containerized **End-to-End Data Pipeline** and Data Warehousing solution designed for the Fast-Moving Consumer Goods (FMCG) and distribution sector in Morocco. The architecture ingests data across heterogeneous formats (CSV, Excel), applies rigorous quality validation and automated quarantine mechanisms, and populates a Star Schema Data Warehouse powering 7 BI Analytical Marts in Power BI.

## 🏗️ Architecture & Data Pipeline Flow

```mermaid
flowchart TD
    subgraph Sources [Raw Data Ingestion]
        S1[sales_YYYY-MM-DD.csv]
        S2[products.xlsx]
        S3[stores.csv]
    end

    subgraph ETL [Python ETL Core]
        E[raw_ingestion.py]
        T[transform_sales.py & Quality Engine]
    end

    subgraph DWH [PostgreSQL Data Warehouse]
        subgraph RawSchema [raw schema]
            R1[(raw_sales)]
        end
        subgraph OpsSchema [ops schema]
            O1[(etl_batch)]
            O2[(etl_file_manifest)]
            O3[(etl_rejected_record)]
        end
        subgraph AnalyticsSchema [analytics schema - Star Schema]
            D1[(dim_store)]
            D2[(dim_product)]
            F1[(fact_sales)]
        end
        subgraph Marts [Analytics Views & Marts]
            V1[vw_daily_sales_by_store]
            V2[vw_sales_by_category]
            V3[vw_product_performance]
            V4[vw_regional_store_ranking]
            V5[vw_basket_analysis]
            V6[vw_rejection_summary]
            V7[vw_data_quality_metrics]
        end
    end

    subgraph Orchestration [Orchestration]
        A[Apache Airflow DAG]
    end

    subgraph BI [Reporting & BI]
        P[Power BI Dashboard]
    end

    Sources --> E --> R1 & O1 & O2
    R1 --> T
    T -- Quality Rejected --> O3
    T -- Clean Records --> F1
    D1 & D2 --> F1
    F1 --> V1 & V2 & V3 & V4 & V5
    O3 --> V6 & V7
    A -. Daily Schedule .-> ETL
    Marts --> P
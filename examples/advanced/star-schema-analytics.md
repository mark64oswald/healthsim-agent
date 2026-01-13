# Star Schema Analytics

Generate dimensional data models for healthcare analytics and reporting.

---

## Goal

Create star schema dimensional models from HealthSim data for use in analytics platforms, data warehouses, and BI tools.

## Prerequisites

- HealthSim Agent with data generated
- Understanding of dimensional modeling concepts
- SQL knowledge for querying

---

## Overview

HealthSim can transform generated data into star schema format with:

- **Dimension tables**: Slowly changing reference data (patients, providers, codes)
- **Fact tables**: Transactional data at specific grain (claims, encounters, labs)

```
                    ┌──────────────┐
                    │  dim_patient │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐
│ dim_provider │────│ fact_claims  │────│   dim_date   │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │ dim_diagnosis│
                    └──────────────┘
```

---

## Example 1: Claims Star Schema

### Step 1: Generate Dimensional Model

```
healthsim › Export my claims data as a star schema
```

Expected output:
```
✓ Generated star schema for claims:

**Dimensions:**
| Table | Rows | Description |
|-------|------|-------------|
| dim_member | 500 | Member demographics |
| dim_provider | 150 | Provider attributes |
| dim_diagnosis | 892 | ICD-10 codes with descriptions |
| dim_procedure | 456 | CPT codes with descriptions |
| dim_date | 731 | Calendar dimension (2 years) |

**Facts:**
| Table | Rows | Grain |
|-------|------|-------|
| fact_claim_line | 12,450 | One row per claim line |

Exported to: ~/healthsim-exports/claims-star-schema/
```

### Step 2: Query the Model

```sql
-- Total paid amount by month and provider specialty
SELECT 
    d.year_month,
    p.specialty,
    COUNT(DISTINCT f.claim_id) as claim_count,
    SUM(f.paid_amount) as total_paid
FROM fact_claim_line f
JOIN dim_date d ON f.service_date_key = d.date_key
JOIN dim_provider p ON f.provider_key = p.provider_key
GROUP BY d.year_month, p.specialty
ORDER BY d.year_month, total_paid DESC;
```

---

## Example 2: Clinical Trial Dimensional Model

### Generate Trial Analytics Schema

```
healthsim › Create a star schema for trial ONCO-2025-001 analytics
```

### Dimension Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `dim_study` | Study/protocol attributes | study_key, study_id, phase, therapeutic_area |
| `dim_site` | Site/geography attributes | site_key, site_id, country, pi_name |
| `dim_subject` | Subject demographics | subject_key, usubjid, age_band, sex |
| `dim_treatment_arm` | Treatment arm definitions | arm_key, arm_code, dose, schedule |
| `dim_visit_schedule` | Protocol visit schedule | visit_key, visit_num, target_day |
| `dim_meddra` | MedDRA hierarchy for AEs | meddra_key, pt_term, soc_term |

### Fact Tables

| Table | Grain | Key Metrics |
|-------|-------|-------------|
| `fact_enrollment` | One row per subject milestone | days_to_randomization, screen_failure_flag |
| `fact_visit` | One row per actual visit | window_deviation_days, assessments_completed |
| `fact_adverse_event` | One row per AE occurrence | severity, ctcae_grade, is_serious |
| `fact_lab_result` | One row per lab result | result_numeric, is_abnormal, change_from_baseline |

### Sample Analytics Queries

```sql
-- Enrollment velocity by site
SELECT 
    s.site_id,
    s.country,
    COUNT(*) as subjects_enrolled,
    AVG(f.days_screen_to_randomization) as avg_days_to_randomize
FROM fact_enrollment f
JOIN dim_site s ON f.site_key = s.site_key
WHERE f.screen_failure_flag = FALSE
GROUP BY s.site_id, s.country
ORDER BY subjects_enrolled DESC;

-- Adverse event rates by treatment arm and SOC
SELECT 
    a.arm_name,
    m.soc_term,
    COUNT(*) as ae_count,
    COUNT(CASE WHEN f.is_serious THEN 1 END) as sae_count
FROM fact_adverse_event f
JOIN dim_treatment_arm a ON f.arm_key = a.arm_key
JOIN dim_meddra m ON f.meddra_key = m.meddra_key
GROUP BY a.arm_name, m.soc_term
ORDER BY ae_count DESC;
```

---

## Example 3: Population Health Model

### Generate SDOH-Enhanced Schema

```
healthsim › Create a population health star schema with SDOH factors
```

### Dimensions

```sql
CREATE TABLE dim_geography (
    geo_key INT PRIMARY KEY,
    zip_code VARCHAR(10),
    county VARCHAR(100),
    state VARCHAR(2),
    cbsa_name VARCHAR(200),
    urban_rural VARCHAR(20),
    svi_overall_percentile DECIMAL(5,2),
    svi_socioeconomic_percentile DECIMAL(5,2),
    svi_housing_percentile DECIMAL(5,2)
);

CREATE TABLE dim_health_indicator (
    indicator_key INT PRIMARY KEY,
    measure_id VARCHAR(50),
    measure_name VARCHAR(200),
    category VARCHAR(100),
    data_source VARCHAR(100)
);
```

### Facts

```sql
CREATE TABLE fact_population_health (
    fact_key INT PRIMARY KEY,
    geo_key INT REFERENCES dim_geography,
    indicator_key INT REFERENCES dim_health_indicator,
    year INT,
    data_value DECIMAL(10,4),
    population_count INT,
    confidence_low DECIMAL(10,4),
    confidence_high DECIMAL(10,4)
);
```

### Analytics Query

```sql
-- Diabetes prevalence vs social vulnerability
SELECT 
    CASE 
        WHEN g.svi_overall_percentile >= 0.75 THEN 'High Vulnerability'
        WHEN g.svi_overall_percentile >= 0.50 THEN 'Moderate'
        ELSE 'Low Vulnerability'
    END as vulnerability_tier,
    AVG(f.data_value) as avg_diabetes_prevalence,
    COUNT(DISTINCT g.county) as county_count
FROM fact_population_health f
JOIN dim_geography g ON f.geo_key = g.geo_key
JOIN dim_health_indicator h ON f.indicator_key = h.indicator_key
WHERE h.measure_id = 'DIABETES'
GROUP BY vulnerability_tier
ORDER BY avg_diabetes_prevalence DESC;
```

---

## Export Formats

### DuckDB (Default)

```
healthsim › Export star schema to DuckDB

✓ Exported to: ~/healthsim-exports/star-schema.duckdb

Connect with:
duckdb ~/healthsim-exports/star-schema.duckdb
```

### Parquet Files

```
healthsim › Export star schema as Parquet files

✓ Exported:
  - dim_member.parquet (125 KB)
  - dim_provider.parquet (45 KB)
  - fact_claim_line.parquet (2.3 MB)
```

### SQL DDL + CSV

```
healthsim › Export star schema with DDL scripts

✓ Exported:
  - schema.sql (DDL statements)
  - dim_*.csv (dimension data)
  - fact_*.csv (fact data)
```

---

## Best Practices

### Grain Definition

| Fact Table | Recommended Grain |
|------------|------------------|
| Claims | One row per claim line |
| Encounters | One row per encounter |
| Labs | One row per result |
| Pharmacy | One row per fill |
| Adverse Events | One row per AE |

### Slowly Changing Dimensions

```sql
-- Type 2 SCD for member dimension
CREATE TABLE dim_member (
    member_key INT PRIMARY KEY,        -- Surrogate key
    member_id VARCHAR(50),             -- Natural key
    name VARCHAR(200),
    plan_code VARCHAR(20),
    effective_date DATE,
    expiration_date DATE,
    is_current BOOLEAN
);
```

---

## Related

- [Cohort Analytics](../intermediate/cohort-analytics.md) - Analyze cohorts
- [Batch Generation](batch-generation.md) - Generate large datasets
- [Full Data Pipeline](full-data-pipeline.md) - End-to-end workflow

---

*Star Schema Analytics v1.0 | HealthSim Agent*

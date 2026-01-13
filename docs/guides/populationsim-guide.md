# PopulationSim Guide

Access real US population health data and create evidence-based cohort specifications through natural conversation.

---

## Overview

PopulationSim provides access to real population health data:

- **CDC PLACES** - Health indicators for every US county and census tract
- **Social Vulnerability Index (SVI)** - SDOH metrics at tract level
- **Area Deprivation Index (ADI)** - Socioeconomic neighborhood rankings
- **Demographics** - Population characteristics by geography

**Key Distinction:** PopulationSim works with **real reference data**, not synthetic data. Use it to understand populations, then generate synthetic individuals with other products.

**Output Formats:** JSON, CSV, SQL query results

---

## Quick Start

Profile a county's health data:

```
healthsim › Profile Harris County, Texas for diabetes

✓ Population Profile: Harris County, TX

  Population:    4,731,145
  
  Health Indicators (CDC PLACES):
    Diabetes Prevalence:        12.8%
    Obesity Prevalence:         32.1%
    High Blood Pressure:        31.5%
    No Health Insurance:        21.3%
  
  Social Vulnerability (SVI):
    Overall SVI:                0.72 (High)
    Socioeconomic:              0.68
    Household/Disability:       0.71
    Minority/Language:          0.89
    Housing/Transportation:     0.58
  
  Top Census Tracts by Diabetes:
    Tract 2301: 18.2%
    Tract 2405: 17.9%
    Tract 1102: 17.4%
```

---

## Data Sources

### CDC PLACES

Community-level health data from the CDC's Population Level Analysis and Community Estimates:

| Category | Measures |
|----------|----------|
| **Prevention** | Checkups, cholesterol screening, mammography |
| **Health Outcomes** | Diabetes, obesity, heart disease, cancer |
| **Risk Behaviors** | Smoking, physical inactivity, binge drinking |
| **Health Status** | Poor mental/physical health days |
| **Disabilities** | Hearing, vision, cognition, mobility |

Available at county and census tract level for all US locations.

### Social Vulnerability Index (SVI)

CDC/ATSDR Social Vulnerability Index measures community resilience:

| Theme | Components |
|-------|------------|
| **Socioeconomic** | Below poverty, unemployed, no high school diploma, uninsured |
| **Household/Disability** | Age 65+, age 17 and under, disability, single-parent |
| **Minority/Language** | Minority status, limited English proficiency |
| **Housing/Transportation** | Multi-unit housing, mobile homes, no vehicle, group quarters |

Scores range from 0 (lowest vulnerability) to 1 (highest vulnerability).

### Area Deprivation Index (ADI)

Neighborhood-level socioeconomic disadvantage:

- National percentile ranking (1-100)
- State-level decile ranking (1-10)
- Based on 17 census indicators

---

## Common Queries

### Geographic Profiling

Profile specific areas:

```
Profile Los Angeles County, California
Show health data for Cook County, Illinois
Profile Miami-Dade County, Florida
Get population health summary for Maricopa County
```

### Health Indicator Queries

Query specific health metrics:

```
What is the diabetes prevalence in Harris County?
Show obesity rates for all Texas counties
Find counties with highest heart disease rates
Compare cancer prevalence across California counties
```

### Social Vulnerability Queries

Query SVI data:

```
What is the social vulnerability of Bronx County?
Find the most socially vulnerable counties in Texas
Show SVI breakdown for Philadelphia County
Compare SVI themes for Los Angeles vs Cook County
```

### Census Tract Level

Drill down to tract level:

```
Show census tracts in Harris County with highest diabetes
Find vulnerable tracts in Los Angeles County
Profile census tract 48201230100 in Houston
```

---

## Building Cohort Specifications

Use population data to design realistic cohorts:

### Evidence-Based Cohort Design

```
Based on Harris County diabetes data, create a cohort specification
for 100 Type 2 diabetic patients matching local demographics
```

Output:
```
✓ Cohort Specification Generated

  Name:          harris-county-diabetics
  Size:          100 patients
  
  Demographics (matching Harris County):
    Age Distribution:   45-64 (45%), 65+ (35%), 18-44 (20%)
    Gender:             52% Female, 48% Male
    Race/Ethnicity:     44% Hispanic, 20% Black, 28% White, 8% Asian
    
  Clinical Profile (based on CDC PLACES):
    Diabetes:           100% (cohort focus)
    Hypertension:       65% (comorbidity rate)
    Obesity:            58% (comorbidity rate)
    High Cholesterol:   45% (comorbidity rate)
    
  SDOH Factors (based on SVI 0.72):
    Uninsured:          21%
    Below Poverty:      18%
    No Vehicle:         12%
```

### Using Specifications

```
Generate patients using the harris-county-diabetics specification
Create 50 patients matching this population profile
```

---

## Comparative Analysis

### County Comparisons

```
Compare diabetes rates: Harris County vs Dallas County vs Bexar County
Show health disparities between Los Angeles and San Bernardino counties
Compare SVI between urban and rural Texas counties
```

### State-Level Analysis

```
Show diabetes prevalence by county for all of Florida
Rank Texas counties by social vulnerability
Find healthiest counties in California
```

### Trend Identification

```
Which counties have the highest chronic disease burden?
Find areas with significant health disparities
Identify underserved communities in Georgia
```

---

## SQL Queries

Access data directly via SQL:

### Population Schema Tables

```sql
-- CDC PLACES county data
SELECT county_name, diabetes_crude_prevalence, obesity_crude_prevalence
FROM population.places_county
WHERE state_abbr = 'TX'
ORDER BY diabetes_crude_prevalence DESC;

-- SVI data
SELECT county, overall_svi, svi_socioeconomic, svi_minority_language
FROM population.svi_county
WHERE state = 'TX' AND overall_svi > 0.7;

-- Census tract data
SELECT tract_fips, diabetes_crude_prevalence, population
FROM population.places_tract
WHERE county_fips = '48201'  -- Harris County
ORDER BY diabetes_crude_prevalence DESC
LIMIT 10;
```

### Using the Query Tool

```
healthsim › /sql SELECT county_name, diabetes_crude_prevalence 
            FROM population.places_county 
            WHERE state_abbr = 'CA' 
            ORDER BY diabetes_crude_prevalence DESC 
            LIMIT 10
```

---

## Integration with Generation

### Driving Patient Generation

```
Profile Harris County for cardiovascular disease,
then generate 50 patients matching that population
```

### Informing Claims Generation

```
Based on uninsured rates in Los Angeles County,
generate a mix of commercial and Medicaid members
```

### Clinical Trial Site Selection

```
Find counties with high cancer rates and adequate
healthcare infrastructure for trial site planning
```

---

## Geographic Queries

### By State

```
Show all counties in Texas with population over 100,000
List Florida counties by diabetes prevalence
Get health summary for California counties
```

### By Region

```
Compare health indicators for Gulf Coast counties
Show SVI for Appalachian region counties
Analyze health disparities in Mississippi Delta counties
```

### By Metro Area

```
Profile Houston metro area (Harris + surrounding counties)
Show health data for DFW metroplex
Analyze Chicago metro area health disparities
```

---

## Available Metrics

### CDC PLACES Health Outcomes

| Metric | Field | Description |
|--------|-------|-------------|
| Diabetes | `diabetes_crude_prevalence` | Adults with diabetes |
| Obesity | `obesity_crude_prevalence` | Adults with BMI ≥30 |
| Heart Disease | `chd_crude_prevalence` | Coronary heart disease |
| Stroke | `stroke_crude_prevalence` | History of stroke |
| Cancer | `cancer_crude_prevalence` | Cancer (excluding skin) |
| COPD | `copd_crude_prevalence` | Chronic lung disease |
| Asthma | `asthma_crude_prevalence` | Current asthma |
| CKD | `kidney_crude_prevalence` | Chronic kidney disease |
| Depression | `depression_crude_prevalence` | Depression diagnosis |

### SVI Themes

| Theme | Field | Description |
|-------|-------|-------------|
| Overall | `overall_svi` | Composite vulnerability |
| Socioeconomic | `svi_socioeconomic` | Economic factors |
| Household | `svi_household_disability` | Household composition |
| Minority | `svi_minority_language` | Minority status/language |
| Housing | `svi_housing_transport` | Housing type/transportation |

---

## Tips & Best Practices

### Start with Geography

```
# First, understand the population
Profile Harris County, Texas

# Then, design your cohort
Based on this profile, create a diabetes cohort specification

# Finally, generate data
Generate 100 patients using this specification
```

### Use Real Data for Realism

```
What is the actual uninsured rate in Los Angeles County?
Use that rate when generating members for this area
```

### Combine Data Sources

```
Show both CDC PLACES health data and SVI vulnerability
for Bronx County to understand the full picture
```

### Drill Down When Needed

```
# County level for overview
Profile Cook County, Illinois

# Tract level for specific targeting
Show most vulnerable census tracts in Cook County
```

---

## Related Resources

### Skills

- [data-sources.md](../../skills/populationsim/data-sources.md)
- [geographic/](../../skills/populationsim/geographic/)
- [sdoh/](../../skills/populationsim/sdoh/)
- [health-patterns/](../../skills/populationsim/health-patterns/)

### Reference

- [Database Schema](../reference/database-schema.md) - Population schema tables
- [Data Architecture](../reference/data-architecture.md) - Reference data details

### Examples

- [County Profiling](../../examples/basic/county-profiling.md)
- [Cohort Design](../../examples/intermediate/cohort-design.md)
- [Population Analytics](../../examples/advanced/population-analytics.md)

---

## Troubleshooting

### County not found

Use standard county names:
```
# Correct
Profile Harris County, Texas

# May not work
Profile Houston, Texas (city, not county)
```

### Census tract queries slow

Use county filter:
```
Show tracts in Harris County with diabetes > 15%
(faster than searching all US tracts)
```

### Missing metrics

Not all metrics available for all areas:
```
Show available health metrics for this county
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.

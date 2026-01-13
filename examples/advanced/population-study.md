# Advanced Example: Population Health Study

This example demonstrates using PopulationSim to design and execute a population-based health study, combining real demographic/health data with synthetic individual generation.

## Scenario

Design a study examining the relationship between social determinants of health (SDOH) and diabetes outcomes in vulnerable populations across three metropolitan areas.

## Step 1: Define Study Geography

```
I want to study diabetes outcomes in vulnerable populations. Help me identify 
census tracts with high social vulnerability in these metro areas:
- Houston, TX
- Chicago, IL  
- Phoenix, AZ

Focus on tracts with:
- High diabetes prevalence (>15%)
- High social vulnerability (SVI > 0.75)
- Population over 3,000
```

### Expected Query Results

```sql
-- HealthSim Agent executes against reference database
SELECT 
    p.state_abbr,
    p.county_name,
    p.census_tract_fips,
    p.diabetes_crude_prev as diabetes_prevalence,
    s.svi_overall,
    s.e_totpop as population,
    s.ep_pov150 as pct_below_150_poverty,
    s.ep_nohsdp as pct_no_hs_diploma
FROM population.places_tract p
JOIN population.svi_tract s ON p.census_tract_fips = s.fips
WHERE p.state_abbr IN ('TX', 'IL', 'AZ')
  AND p.county_name IN ('Harris', 'Cook', 'Maricopa')
  AND p.diabetes_crude_prev > 15
  AND s.svi_overall > 0.75
  AND s.e_totpop > 3000
ORDER BY p.diabetes_crude_prev DESC
LIMIT 20;
```

**Results Summary:**

| Metro | Tracts Found | Avg Diabetes % | Avg SVI | Total Pop |
|-------|-------------|----------------|---------|-----------|
| Houston | 42 | 18.2% | 0.82 | 185,000 |
| Chicago | 38 | 17.5% | 0.84 | 156,000 |
| Phoenix | 28 | 16.8% | 0.79 | 112,000 |

## Step 2: Analyze SDOH Factors

```
For the high-vulnerability tracts identified, analyze the relationship between 
SDOH factors and health outcomes. Show me:
- Correlation between poverty and diabetes
- Healthcare access metrics
- Food insecurity indicators
- Transportation barriers
```

### Expected Analysis Output

```json
{
  "sdoh_analysis": {
    "study_population": {
      "total_tracts": 108,
      "total_population": 453000,
      "geographic_distribution": {
        "Houston": {"tracts": 42, "population": 185000},
        "Chicago": {"tracts": 38, "population": 156000},
        "Phoenix": {"tracts": 28, "population": 112000}
      }
    },
    "health_indicators": {
      "diabetes_prevalence": {
        "mean": 17.5,
        "std": 2.8,
        "range": [15.1, 24.2]
      },
      "obesity_prevalence": {
        "mean": 38.2,
        "std": 5.1,
        "range": [28.4, 48.6]
      },
      "no_health_insurance": {
        "mean": 22.4,
        "std": 8.2,
        "range": [8.5, 42.1]
      }
    },
    "sdoh_correlations": {
      "poverty_vs_diabetes": {
        "correlation": 0.68,
        "p_value": "<0.001",
        "interpretation": "Strong positive correlation"
      },
      "no_vehicle_vs_diabetes": {
        "correlation": 0.52,
        "p_value": "<0.001",
        "interpretation": "Moderate positive correlation"
      },
      "food_desert_vs_diabetes": {
        "correlation": 0.44,
        "p_value": "<0.001",
        "interpretation": "Moderate positive correlation"
      }
    },
    "vulnerability_themes": {
      "socioeconomic": {
        "avg_score": 0.78,
        "key_factors": ["Poverty", "Unemployment", "No high school diploma"]
      },
      "household_disability": {
        "avg_score": 0.72,
        "key_factors": ["Single-parent households", "Disability", "Age 65+"]
      },
      "minority_language": {
        "avg_score": 0.81,
        "key_factors": ["Minority status", "Limited English"]
      },
      "housing_transportation": {
        "avg_score": 0.69,
        "key_factors": ["Multi-unit housing", "No vehicle", "Group quarters"]
      }
    }
  }
}
```

## Step 3: Design Cohort Specifications

```
Based on this analysis, design specifications for a synthetic study cohort of 
1,000 patients that reflects the vulnerable population characteristics:
- Demographics matching tract distributions
- Health conditions reflecting prevalence data
- SDOH factors representing vulnerability themes
- Include diabetes subgroups: controlled, uncontrolled, newly diagnosed
```

### Expected Cohort Specification

```json
{
  "cohort_specification": {
    "name": "SDOH-Diabetes-VulnerablePop-Study",
    "size": 1000,
    "source_geography": {
      "tracts": 108,
      "metros": ["Houston", "Chicago", "Phoenix"],
      "allocation": "proportional_to_population"
    },
    "demographic_targets": {
      "age_distribution": {
        "18-34": 0.15,
        "35-49": 0.25,
        "50-64": 0.35,
        "65+": 0.25
      },
      "sex": {"female": 0.54, "male": 0.46},
      "race_ethnicity": {
        "hispanic": 0.42,
        "black": 0.28,
        "white": 0.22,
        "other": 0.08
      }
    },
    "diabetes_subgroups": {
      "well_controlled": {
        "proportion": 0.30,
        "hba1c_range": [6.5, 7.0],
        "complications": "minimal"
      },
      "moderately_controlled": {
        "proportion": 0.35,
        "hba1c_range": [7.0, 8.5],
        "complications": "some"
      },
      "poorly_controlled": {
        "proportion": 0.25,
        "hba1c_range": [8.5, 12.0],
        "complications": "common"
      },
      "newly_diagnosed": {
        "proportion": 0.10,
        "hba1c_range": [6.5, 9.0],
        "duration_months": [0, 6]
      }
    },
    "sdoh_factors": {
      "income": {
        "below_poverty": 0.35,
        "150_percent_poverty": 0.55,
        "above_150": 0.10
      },
      "insurance_status": {
        "uninsured": 0.22,
        "medicaid": 0.38,
        "medicare": 0.25,
        "commercial": 0.15
      },
      "food_access": {
        "food_secure": 0.45,
        "low_food_security": 0.35,
        "very_low_food_security": 0.20
      },
      "transportation": {
        "personal_vehicle": 0.55,
        "public_transit": 0.30,
        "no_reliable_transport": 0.15
      }
    },
    "comorbidities": {
      "obesity": 0.62,
      "hypertension": 0.58,
      "hyperlipidemia": 0.45,
      "ckd": 0.22,
      "depression": 0.28
    }
  }
}
```

## Step 4: Generate Synthetic Individuals

```
Generate the 1,000-patient cohort based on the specifications. Include:
- Complete demographics and contact info
- Medical history with diagnosis dates
- Current medications
- Recent lab values
- SDOH assessment results
- Care utilization patterns
```

### Expected Output (Sample Patients)

```json
{
  "patients": [
    {
      "patient_id": "SDOH-DM-0001",
      "demographics": {
        "first_name": "Maria",
        "last_name": "Rodriguez",
        "dob": "1968-03-15",
        "age": 56,
        "sex": "F",
        "race": "Other",
        "ethnicity": "Hispanic or Latino",
        "preferred_language": "Spanish"
      },
      "geography": {
        "census_tract": "48201313400",
        "county": "Harris",
        "state": "TX",
        "metro": "Houston"
      },
      "diabetes_status": {
        "subgroup": "poorly_controlled",
        "diagnosis_date": "2015-08-22",
        "duration_years": 9,
        "type": "Type 2"
      },
      "clinical_data": {
        "most_recent_hba1c": {
          "value": 9.8,
          "date": "2024-11-15"
        },
        "bmi": 34.2,
        "blood_pressure": "148/92",
        "egfr": 52
      },
      "comorbidities": [
        {"condition": "Essential hypertension", "icd10": "I10", "onset": "2012-03-10"},
        {"condition": "Obesity", "icd10": "E66.9", "onset": "2008-01-01"},
        {"condition": "CKD Stage 3a", "icd10": "N18.31", "onset": "2022-06-15"},
        {"condition": "Major depressive disorder", "icd10": "F32.1", "onset": "2019-11-20"}
      ],
      "medications": [
        {"name": "Metformin", "dose": "1000mg", "frequency": "BID"},
        {"name": "Glipizide", "dose": "10mg", "frequency": "BID"},
        {"name": "Lisinopril", "dose": "40mg", "frequency": "QD"},
        {"name": "Sertraline", "dose": "100mg", "frequency": "QD"}
      ],
      "sdoh_assessment": {
        "income_level": "below_poverty",
        "insurance": "Medicaid",
        "food_security": "low_food_security",
        "transportation": "public_transit",
        "housing": "renter_unstable",
        "health_literacy": "limited",
        "social_support": "limited"
      },
      "care_utilization": {
        "pcp_visits_last_year": 2,
        "endocrinologist_visits_last_year": 0,
        "er_visits_last_year": 3,
        "hospitalizations_last_year": 1,
        "missed_appointments": 4,
        "barriers": ["Transportation", "Work schedule", "Childcare"]
      }
    },
    {
      "patient_id": "SDOH-DM-0002",
      "demographics": {
        "first_name": "James",
        "last_name": "Washington",
        "dob": "1975-11-28",
        "age": 49,
        "sex": "M",
        "race": "Black or African American",
        "ethnicity": "Not Hispanic or Latino",
        "preferred_language": "English"
      },
      "geography": {
        "census_tract": "17031842000",
        "county": "Cook",
        "state": "IL",
        "metro": "Chicago"
      },
      "diabetes_status": {
        "subgroup": "newly_diagnosed",
        "diagnosis_date": "2024-08-10",
        "duration_years": 0,
        "type": "Type 2"
      },
      "clinical_data": {
        "most_recent_hba1c": {
          "value": 7.8,
          "date": "2024-11-01"
        },
        "bmi": 31.5,
        "blood_pressure": "138/88",
        "egfr": 85
      },
      "comorbidities": [
        {"condition": "Essential hypertension", "icd10": "I10", "onset": "2020-05-15"},
        {"condition": "Obesity", "icd10": "E66.9", "onset": "2015-01-01"}
      ],
      "medications": [
        {"name": "Metformin", "dose": "500mg", "frequency": "BID"},
        {"name": "Amlodipine", "dose": "5mg", "frequency": "QD"}
      ],
      "sdoh_assessment": {
        "income_level": "150_percent_poverty",
        "insurance": "uninsured",
        "food_security": "food_secure",
        "transportation": "personal_vehicle",
        "housing": "renter_stable",
        "health_literacy": "adequate",
        "social_support": "moderate"
      },
      "care_utilization": {
        "pcp_visits_last_year": 3,
        "endocrinologist_visits_last_year": 0,
        "er_visits_last_year": 1,
        "hospitalizations_last_year": 0,
        "missed_appointments": 1,
        "barriers": ["Cost", "Work schedule"]
      }
    }
  ]
}
```

## Step 5: Generate Longitudinal Claims Data

```
Using MemberSim, generate 12 months of claims data for these patients:
- Professional claims (physician visits)
- Facility claims (ER, inpatient)
- Pharmacy claims
- Include appropriate diagnoses and procedures
- Reflect care utilization patterns from SDOH factors
```

### Cross-Product Integration

```json
{
  "cross_product_workflow": {
    "source": "PopulationSim cohort",
    "target": "MemberSim claims",
    "correlation": {
      "method": "SSN-based identity linking",
      "patient_to_member_mapping": "1:1"
    },
    "claims_summary": {
      "period": "2024-01-01 to 2024-12-31",
      "total_patients": 1000,
      "claims_generated": {
        "professional": 8420,
        "facility_outpatient": 1250,
        "facility_inpatient": 180,
        "pharmacy": 15600
      },
      "total_allowed": "$4,850,000",
      "total_paid": "$3,920,000",
      "member_responsibility": "$930,000"
    }
  }
}
```

## Step 6: Analyze Outcomes by SDOH Factors

```
Analyze the relationship between SDOH factors and:
- Healthcare costs
- ER utilization
- Medication adherence
- Glycemic control (HbA1c)
Create summary tables for the study report.
```

### Expected Analysis Output

```json
{
  "outcomes_analysis": {
    "by_insurance_status": {
      "uninsured": {
        "n": 220,
        "avg_hba1c": 9.2,
        "pct_controlled": 0.18,
        "er_visits_per_1000": 850,
        "avg_annual_cost": "$2,100",
        "medication_adherence": 0.52
      },
      "medicaid": {
        "n": 380,
        "avg_hba1c": 8.4,
        "pct_controlled": 0.32,
        "er_visits_per_1000": 620,
        "avg_annual_cost": "$5,200",
        "medication_adherence": 0.68
      },
      "medicare": {
        "n": 250,
        "avg_hba1c": 7.8,
        "pct_controlled": 0.45,
        "er_visits_per_1000": 480,
        "avg_annual_cost": "$6,800",
        "medication_adherence": 0.75
      },
      "commercial": {
        "n": 150,
        "avg_hba1c": 7.4,
        "pct_controlled": 0.58,
        "er_visits_per_1000": 220,
        "avg_annual_cost": "$4,100",
        "medication_adherence": 0.82
      }
    },
    "by_food_security": {
      "food_secure": {
        "n": 450,
        "avg_hba1c": 7.6,
        "pct_controlled": 0.48
      },
      "low_food_security": {
        "n": 350,
        "avg_hba1c": 8.5,
        "pct_controlled": 0.28
      },
      "very_low_food_security": {
        "n": 200,
        "avg_hba1c": 9.4,
        "pct_controlled": 0.15
      }
    },
    "by_transportation": {
      "personal_vehicle": {
        "n": 550,
        "missed_appointments_pct": 0.08,
        "pct_controlled": 0.45
      },
      "public_transit": {
        "n": 300,
        "missed_appointments_pct": 0.18,
        "pct_controlled": 0.32
      },
      "no_reliable_transport": {
        "n": 150,
        "missed_appointments_pct": 0.35,
        "pct_controlled": 0.18
      }
    },
    "key_findings": [
      "Uninsured patients have 4x higher ER utilization vs commercially insured",
      "Food insecurity associated with 1.8% higher average HbA1c",
      "Transportation barriers correlate with 4x higher missed appointment rate",
      "SDOH composite score explains 42% of variance in glycemic control"
    ]
  }
}
```

## Export Options

```
Export this study data for:
1. REDCap import (for clinical research database)
2. FHIR Bundles (for EHR integration testing)
3. CSV flat files (for statistical analysis)
4. Study report PDF
```

## Key Learnings

1. **Real Data Foundation**: PopulationSim queries actual CDC/Census data to inform realistic cohort design
2. **SDOH Integration**: Vulnerability indices provide scientifically-grounded SDOH modeling
3. **Cross-Product Correlation**: Patient identities flow seamlessly to MemberSim for claims generation
4. **Geographic Precision**: Census tract-level data enables neighborhood-specific health patterns
5. **Research-Ready Output**: Multiple export formats support diverse analytical workflows

## Related Resources

- [PopulationSim Guide](../docs/guides/populationsim-guide.md)
- [Cross-Product Guide](../docs/guides/cross-product-guide.md)
- [Data Sources Skill](../skills/populationsim/data-sources.md)
- [SDOH Skills](../skills/populationsim/sdoh/)

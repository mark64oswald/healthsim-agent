# Provider Search Example

Search and query real provider data from NPPES.

---

## Goal

Learn how to search the NPPES provider database for real NPIs, specialties, and geographic coverage.

---

## Prerequisites

- HealthSim installed (`pip install healthsim-agent`)
- Database with NPPES data loaded

---

## Steps

### Step 1: Start HealthSim

```bash
healthsim
```

### Step 2: Search by Specialty and Location

```
healthsim › Find cardiologists in Houston, Texas
```

Expected output:
```
✓ Found 847 providers

  Cardiologists in Houston, TX (showing first 10):
  
  │ NPI        │ Name                    │ Specialty           │ Address              │
  ├────────────┼─────────────────────────┼─────────────────────┼──────────────────────┤
  │ 1234567890 │ SMITH, JOHN MD          │ Cardiovascular Dis  │ 1234 Medical Pkwy    │
  │ 1234567891 │ JOHNSON, MARIA MD       │ Cardiovascular Dis  │ 5678 Heart Center Dr │
  │ 1234567892 │ WILLIAMS, ROBERT DO     │ Interventional Card │ 9012 Texas Med Ctr   │
  │ 1234567893 │ BROWN, SARAH MD         │ Cardiovascular Dis  │ 3456 Memorial Dr     │
  │ 1234567894 │ GARCIA, CARLOS MD       │ Electrophysiology   │ 7890 Methodist Way   │
  │ 1234567895 │ MARTINEZ, ANA MD        │ Cardiovascular Dis  │ 2345 Hermann Dr      │
  │ 1234567896 │ DAVIS, MICHAEL MD       │ Interventional Card │ 6789 St Luke's Blvd  │
  │ 1234567897 │ WILSON, JENNIFER MD     │ Cardiovascular Dis  │ 1357 Baylor Plaza    │
  │ 1234567898 │ ANDERSON, DAVID DO      │ Cardiovascular Dis  │ 2468 Clear Lake      │
  │ 1234567899 │ TAYLOR, LISA MD         │ Nuclear Cardiology  │ 3579 Galleria Area   │
  
  Total Results: 847 (showing 10)
  Use: "show more" or filter further
```

### Step 3: Search Facilities

```
healthsim › Find hospitals in Dallas County
```

Expected output:
```
✓ Found 38 hospitals

  Hospitals in Dallas County, TX:
  
  │ NPI        │ Name                          │ Type              │ Beds │
  ├────────────┼───────────────────────────────┼───────────────────┼──────┤
  │ 1111111111 │ BAYLOR UNIVERSITY MED CTR     │ General Acute     │ 914  │
  │ 2222222222 │ PARKLAND HEALTH               │ General Acute     │ 862  │
  │ 3333333333 │ UT SOUTHWESTERN MED CTR       │ Teaching Hospital │ 740  │
  │ 4444444444 │ METHODIST DALLAS MED CTR      │ General Acute     │ 595  │
  │ 5555555555 │ TEXAS HEALTH PRESBYTERIAN     │ General Acute     │ 898  │
  │ 6666666666 │ MEDICAL CITY DALLAS           │ General Acute     │ 702  │
  │ 7777777777 │ CHILDREN'S MEDICAL CTR        │ Children's Hosp   │ 559  │
  ...
  
  Total: 38 facilities
```

### Step 4: Lookup Specific NPI

```
healthsim › Lookup NPI 1234567890
```

Expected output:
```
Provider Details - NPI 1234567890
═══════════════════════════════════════

  Name:           JOHN SMITH, MD
  Entity Type:    Individual (Type 1)
  Gender:         Male
  
  Primary Taxonomy:
    Code:    207RC0000X
    Desc:    Cardiovascular Disease
    Primary: Yes
    State:   TX
  
  Practice Address:
    1234 Medical Parkway, Suite 500
    Houston, TX 77030
    Phone: (713) 555-1234
    Fax:   (713) 555-1235
  
  Mailing Address:
    Same as practice
  
  Identifiers:
    License: TX-12345 (State: TX)
    Medicare: I12345
  
  Enumeration Date: 2008-04-15
  Last Update:      2023-11-20
  Status:           Active
```

### Step 5: Search by Taxonomy Code

```
healthsim › Find all Family Medicine providers in Austin (207Q00000X)
```

Expected output:
```
✓ Found 1,234 Family Medicine providers in Austin, TX

  Taxonomy: 207Q00000X - Family Medicine
  
  Geographic Distribution:
    Downtown Austin:     187 (15%)
    North Austin:        312 (25%)
    South Austin:        289 (23%)
    East Austin:         156 (13%)
    West Austin:         178 (14%)
    Round Rock/Cedar:    112 (10%)
  
  Entity Types:
    Individual (Type 1): 1,098 (89%)
    Organization (Type 2): 136 (11%)
  
  Top Organizations:
    • Austin Regional Clinic: 45 providers
    • Seton Family Medicine: 28 providers
    • St. David's Primary: 22 providers
```

### Step 6: Network Adequacy Analysis

```
healthsim › Analyze provider coverage for Harris County
```

Expected output:
```
Network Adequacy Analysis - Harris County, TX
═══════════════════════════════════════════════

  Population:     4.7 million
  Land Area:      1,777 sq mi
  
  Provider Ratios:
  │ Specialty           │ Providers │ Per 100K │ Benchmark│ Status │
  ├─────────────────────┼───────────┼──────────┼──────────┼────────┤
  │ Primary Care        │ 4,521     │ 96.2     │ 60-80    │ ✓ Met  │
  │ Cardiology          │ 847       │ 18.0     │ 10-15    │ ✓ Met  │
  │ Mental Health       │ 1,234     │ 26.3     │ 30-40    │ ⚠ Low  │
  │ OB/GYN             │ 678       │ 14.4     │ 12-15    │ ✓ Met  │
  │ Pediatrics          │ 892       │ 19.0     │ 15-20    │ ✓ Met  │
  │ Endocrinology       │ 156       │ 3.3      │ 3-5      │ ✓ Met  │
  │ Orthopedics         │ 445       │ 9.5      │ 8-12     │ ✓ Met  │
  
  Access Gaps:
    ⚠ Mental Health providers below benchmark
    ⚠ Southeast quadrant underserved for Primary Care
```

### Step 7: Export Provider List

```
healthsim › Export Houston cardiologists to CSV
```

Expected output:
```
✓ Exported 847 providers → output/houston-cardiologists.csv

  Columns:
    npi, name, credential, specialty, taxonomy_code,
    address_1, city, state, zip, phone, fax,
    enumeration_date, last_update
  
  File size: 142 KB
```

---

## What You Learned

| Query Type | Results | Use Case |
|------------|---------|----------|
| Specialty + Location | 847 | Find providers for network |
| Facility search | 38 | Hospital roster |
| NPI lookup | 1 | Verify specific provider |
| Taxonomy search | 1,234 | Specialty analysis |
| Adequacy analysis | Summary | Network planning |

---

## Variations

### Search rural areas

```
Find all providers within 50 miles of rural ZIP 79501
```

### Search by credential

```
Find all DO (osteopathic) physicians in Florida
```

### Find pharmacies

```
Find retail pharmacies in San Antonio with 340B status
```

### Find nursing facilities

```
Find skilled nursing facilities in LA County with 100+ beds
```

---

## Common Issues

### Too many results

```
Filter to specific city or limit: "Find first 100 cardiologists in Texas"
```

### Provider not found

Check: NPI format is 10 digits, provider is active and enumerated

### Need quality metrics

```
Show hospital quality ratings for Memorial Hospital NPI 1234567890
```

---

## Related Examples

- [Patient Generation](patient-generation.md) - Use providers in encounters
- [Claims Generation](claims-generation.md) - Reference NPIs in claims
- [Network Analysis](../intermediate/cohort-analysis.md) - Population-based analysis

---

## Related Guides

- [NetworkSim Guide](../../docs/guides/networksim-guide.md) - Complete provider reference
- [Database Schema](../../docs/reference/healthsim-duckdb-schema.md) - Provider tables

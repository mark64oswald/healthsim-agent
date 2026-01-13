# NetworkSim Guide

Query real US healthcare provider data and generate synthetic provider networks through natural conversation.

---

## Overview

NetworkSim provides two capabilities:

1. **Real Provider Data** - Query 8.9 million providers from the NPPES registry
2. **Synthetic Generation** - Create fictional providers, facilities, and pharmacies

**Data Sources:**
- **NPPES** - National Plan and Provider Enumeration System (real NPIs)
- **CMS** - Medicare enrollment and specialty data
- **Taxonomy** - Healthcare Provider Taxonomy codes

**Output Formats:** JSON, CSV, SQL query results

---

## Quick Start

Find real providers:

```
healthsim › Find cardiologists in Houston, Texas

✓ Found 847 providers

  Top Results:
  
  1. John Smith, MD
     NPI:        1234567890
     Specialty:  Cardiovascular Disease
     Address:    1234 Medical Center Dr, Houston, TX 77030
     Practice:   Houston Heart Associates
     
  2. Sarah Johnson, MD  
     NPI:        1234567891
     Specialty:  Interventional Cardiology
     Address:    5678 Heart Way, Houston, TX 77025
     Practice:   Texas Cardiology Group
     
  ... showing 10 of 847 results
```

---

## Real Provider Queries

### By Specialty

Find providers by specialty:

```
Find family medicine doctors in Los Angeles
Search for orthopedic surgeons in Chicago
Find pediatricians in Miami
Search for oncologists in Houston
```

### By Location

Search geographic areas:

```
Find all providers in Harris County, Texas
Search for doctors within 10 miles of ZIP 77030
Find providers in the Dallas-Fort Worth area
Search for specialists in California
```

### By Provider Type

Filter by entity type:

```
Find individual physicians in Phoenix
Search for group practices in Atlanta
Find hospital-based providers in Boston
Search for solo practitioners in Denver
```

### Combined Searches

Multiple criteria:

```
Find female cardiologists in Houston
Search for Spanish-speaking primary care doctors in Miami
Find board-certified oncologists accepting Medicare in LA
Search for providers affiliated with MD Anderson
```

---

## Provider Details

### NPI Information

Query specific providers:

```
Look up NPI 1234567890
Show details for this provider
Find all providers at this practice
```

### Provider Attributes

Available data fields:

| Field | Description |
|-------|-------------|
| NPI | National Provider Identifier |
| Name | Provider name (individual or organization) |
| Entity Type | Individual (Type 1) or Organization (Type 2) |
| Specialty | Primary and secondary taxonomies |
| Address | Practice location(s) |
| Phone | Contact information |
| Gender | For individual providers |
| Credentials | MD, DO, NP, PA, etc. |

### Specialty Taxonomy

Healthcare Provider Taxonomy codes:

```
Find providers with taxonomy 207RC0000X (Cardiovascular Disease)
Search for all internal medicine subspecialties
List taxonomy codes for surgical specialties
```

Common taxonomy mappings:

| Specialty | Taxonomy Code |
|-----------|---------------|
| Family Medicine | 207Q00000X |
| Internal Medicine | 207R00000X |
| Cardiology | 207RC0000X |
| Orthopedics | 207X00000X |
| Pediatrics | 208000000X |
| General Surgery | 208600000X |

---

## Facility Queries

### Hospitals

```
Find hospitals in Harris County
Search for trauma centers in Los Angeles
Find academic medical centers in Texas
Search for children's hospitals in California
```

### Clinics and Centers

```
Find urgent care centers in Phoenix
Search for dialysis facilities in Florida
Find cancer treatment centers in Houston
Search for rehabilitation facilities in Chicago
```

### Pharmacy Locations

```
Find pharmacies in ZIP 77030
Search for specialty pharmacies in Los Angeles
Find 24-hour pharmacies in Miami
Search for compounding pharmacies in Dallas
```

---

## Network Analysis

### Network Adequacy

Analyze provider availability:

```
Analyze network adequacy for cardiology in Harris County
Check if there are enough PCPs for the population in LA
Assess specialist availability in rural Texas counties
```

### Geographic Distribution

```
Map provider distribution in Harris County
Show provider density by ZIP code in Los Angeles
Identify underserved areas in Florida
```

### Travel Distance

```
Find the nearest cardiologist to ZIP 77001
Calculate average distance to oncologist in rural Texas
Identify areas more than 30 miles from a hospital
```

---

## Synthetic Provider Generation

### When to Use Synthetic

Use synthetic providers when:
- Testing applications without real NPI data
- Creating fictional scenarios
- Need providers that don't exist in reality
- Building demo environments

### Generate Providers

```
Generate 10 synthetic primary care providers in Houston
Create a fictional cardiology group practice
Generate synthetic providers for a rural network
```

### Generate Facilities

```
Generate a synthetic 200-bed hospital
Create fictional urgent care centers
Generate a synthetic pharmacy network
```

### Provider Networks

```
Generate a synthetic PPO network for Texas
Create a narrow network of specialists
Generate an ACO provider roster
```

---

## SQL Queries

Direct database access:

### NPPES Tables

```sql
-- Find providers by specialty
SELECT npi, provider_name, specialty_1, city, state
FROM network.nppes_providers
WHERE state = 'TX' 
  AND specialty_1 LIKE '%Cardio%'
  AND entity_type = '1'  -- Individual
ORDER BY city
LIMIT 100;

-- Count providers by specialty in county
SELECT specialty_1, COUNT(*) as count
FROM network.nppes_providers
WHERE state = 'TX' AND county = 'Harris'
GROUP BY specialty_1
ORDER BY count DESC;

-- Find organizations
SELECT npi, organization_name, city
FROM network.nppes_providers
WHERE entity_type = '2'  -- Organization
  AND state = 'CA'
  AND organization_name LIKE '%Hospital%';
```

### Using the Query Tool

```
healthsim › /sql SELECT specialty_1, COUNT(*) as provider_count 
            FROM network.nppes_providers 
            WHERE state = 'TX' AND city = 'HOUSTON' 
            GROUP BY specialty_1 
            ORDER BY provider_count DESC 
            LIMIT 20
```

---

## Integration Scenarios

### Building Provider Networks

```
Create a provider directory for a Texas health plan:
- Find all PCPs in the DFW area
- Add cardiologists and orthopedists as specialists
- Include major hospital systems
```

### Claims Integration

```
Find a real cardiologist NPI in Houston to use
for generating realistic professional claims
```

### Patient Attribution

```
Find PCPs near ZIP 77030 for patient attribution
to primary care providers
```

### Referral Networks

```
Build a referral network:
- PCPs in central Houston
- Connected to specialists at Texas Medical Center
```

---

## Provider Type Reference

### Entity Types

| Type | Code | Description |
|------|------|-------------|
| Individual | 1 | Single provider (physician, NP, PA) |
| Organization | 2 | Group, facility, or health system |

### Common Specialties

| Category | Examples |
|----------|----------|
| Primary Care | Family Medicine, Internal Medicine, Pediatrics |
| Medical Specialties | Cardiology, Gastroenterology, Pulmonology |
| Surgical Specialties | General Surgery, Orthopedics, Cardiothoracic |
| Hospital-Based | Emergency Medicine, Hospitalist, Intensivist |
| Behavioral Health | Psychiatry, Psychology, Social Work |

### Credential Types

| Credential | Description |
|------------|-------------|
| MD | Doctor of Medicine |
| DO | Doctor of Osteopathic Medicine |
| NP | Nurse Practitioner |
| PA | Physician Assistant |
| DPM | Doctor of Podiatric Medicine |
| DC | Doctor of Chiropractic |

---

## Tips & Best Practices

### Use Real Data When Appropriate

```
# For realistic scenarios, query real providers
Find actual cardiologists in Houston for this claims scenario

# For testing/demos, generate synthetic
Generate fictional providers for the demo environment
```

### Narrow Your Searches

```
# Too broad (slow)
Find all doctors in Texas

# Better (faster, more relevant)
Find family medicine doctors in Harris County, Texas
```

### Combine with Population Data

```
# Use PopulationSim to understand the area
Profile Harris County health indicators

# Then find appropriate providers
Find diabetes specialists and endocrinologists in Harris County
```

### Verify Real NPIs

```
# When using real NPIs, verify they're active
Check if NPI 1234567890 is currently active
Show Medicare enrollment status for this provider
```

---

## Related Resources

### Skills

- [query/](../../skills/networksim/query/) - Provider query patterns
- [analytics/](../../skills/networksim/analytics/) - Network analysis
- [synthetic/](../../skills/networksim/synthetic/) - Synthetic generation

### Reference

- [Database Schema](../reference/database-schema.md) - Network schema tables
- [Code Systems](../reference/code-systems.md) - NPI, Taxonomy codes

### Examples

- [Provider Search](../../examples/basic/provider-search.md)
- [Network Analysis](../../examples/intermediate/network-analysis.md)
- [Network Generation](../../examples/advanced/network-generation.md)

---

## Troubleshooting

### No results found

Broaden the search:
```
# Too specific
Find interventional cardiologists specializing in TAVR in rural Montana

# Broader
Find cardiologists in Montana
```

### Slow queries

Add filters:
```
# Slow (searches entire US)
Find all cardiologists

# Faster (limited geography)
Find cardiologists in Houston, Texas
```

### Outdated information

NPPES data is periodically updated:
```
Note: Provider data reflects NPPES as of [date].
Individual providers should be verified for current status.
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.

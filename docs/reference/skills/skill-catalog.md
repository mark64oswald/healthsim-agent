# Skill Catalog

Complete index of all HealthSim skills organized by product and category.

## Summary

| Product | Skills | Primary Focus |
|---------|--------|---------------|
| **PopulationSim** | 52 | Demographics, geography, health patterns |
| **Generation** | 47 | Generation framework patterns |
| **NetworkSim** | 44 | Providers, facilities, networks |
| **TrialSim** | 24 | Clinical trials, CDISC |
| **PatientSim** | 23 | Clinical data, encounters |
| **RxMemberSim** | 10 | Pharmacy, formularies |
| **MemberSim** | 10 | Claims, eligibility |
| **Common** | 5 | Shared utilities |
| **Total** | **216** | |

---

## PatientSim Skills

Clinical data generation for EMR/EHR systems.

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | PatientSim master skill |
| `README.md` | Product overview |

### Clinical Encounters
| Skill | Description |
|-------|-------------|
| `encounters/emergency-visit.md` | Emergency department encounters |
| `encounters/inpatient-stay.md` | Hospital admissions |
| `encounters/outpatient-visit.md` | Office/clinic visits |
| `encounters/telehealth.md` | Virtual care encounters |

### Conditions
| Skill | Description |
|-------|-------------|
| `conditions/chronic-conditions.md` | Long-term condition management |
| `conditions/acute-conditions.md` | Short-term illnesses |
| `conditions/comorbidities.md` | Multi-condition patterns |

### Clinical Data
| Skill | Description |
|-------|-------------|
| `clinical/vital-signs.md` | BP, HR, temp, resp, O2 |
| `clinical/lab-results.md` | Laboratory test patterns |
| `clinical/medications.md` | Medication orders |
| `clinical/procedures.md` | Clinical procedures |
| `clinical/immunizations.md` | Vaccine records |

### Specialized Areas
| Skill | Description |
|-------|-------------|
| `specialty/cardiology.md` | Cardiac care patterns |
| `specialty/diabetes.md` | Diabetes management |
| `specialty/oncology.md` | Cancer care |
| `specialty/maternal.md` | OB/GYN care |
| `specialty/pediatrics.md` | Pediatric care |
| `specialty/behavioral.md` | Mental health |

---

## MemberSim Skills

Payer/claims data generation.

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | MemberSim master skill |
| `README.md` | Product overview |

### Claims
| Skill | Description |
|-------|-------------|
| `professional-claims.md` | 837P professional claims |
| `facility-claims.md` | 837I institutional claims |

### Enrollment & Eligibility
| Skill | Description |
|-------|-------------|
| `enrollment-eligibility.md` | 834 enrollment, eligibility |
| `plan-benefits.md` | Benefit structures |
| `accumulator-tracking.md` | Deductible, OOP tracking |

### Utilization
| Skill | Description |
|-------|-------------|
| `prior-authorization.md` | Prior auth workflows |
| `behavioral-health.md` | BH carve-out claims |
| `value-based-care.md` | VBC arrangements |

---

## RxMemberSim Skills

Pharmacy/PBM data generation.

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | RxMemberSim master skill |
| `README.md` | Product overview |

### Pharmacy Claims
| Skill | Description |
|-------|-------------|
| `retail-pharmacy.md` | Retail Rx claims |
| `specialty-pharmacy.md` | Specialty drug claims |

### Drug Management
| Skill | Description |
|-------|-------------|
| `formulary-management.md` | Formulary tiers, PA |
| `dur-alerts.md` | Drug utilization review |
| `rx-prior-auth.md` | Pharmacy prior auth |

### Benefits & Programs
| Skill | Description |
|-------|-------------|
| `rx-enrollment.md` | Pharmacy benefit enrollment |
| `rx-accumulator.md` | Rx accumulators |
| `manufacturer-programs.md` | Copay cards, patient assistance |

---

## TrialSim Skills

Clinical trial data generation (CDISC).

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | TrialSim master skill |
| `README.md` | Product overview |
| `clinical-trials-domain.md` | Domain overview |

### Trial Phases
| Skill | Description |
|-------|-------------|
| `phase1-dose-escalation.md` | Phase 1 dose-finding |
| `phase2-proof-of-concept.md` | Phase 2 efficacy |
| `phase3-pivotal.md` | Phase 3 registration |
| `recruitment-enrollment.md` | Subject recruitment |

### SDTM Domains
| Skill | Description |
|-------|-------------|
| `domains/demographics-dm.md` | DM domain |
| `domains/disposition-ds.md` | DS domain |
| `domains/adverse-events-ae.md` | AE domain |
| `domains/concomitant-meds-cm.md` | CM domain |
| `domains/exposure-ex.md` | EX domain |
| `domains/laboratory-lb.md` | LB domain |
| `domains/vital-signs-vs.md` | VS domain |
| `domains/medical-history-mh.md` | MH domain |

### Therapeutic Areas
| Skill | Description |
|-------|-------------|
| `therapeutic-areas/oncology.md` | Oncology trials |
| `therapeutic-areas/cardiovascular.md` | CV trials |
| `therapeutic-areas/cns.md` | CNS/neuro trials |
| `therapeutic-areas/cgt.md` | Cell/gene therapy |

### Real-World Evidence
| Skill | Description |
|-------|-------------|
| `rwe/overview.md` | RWE concepts |
| `rwe/synthetic-control.md` | Synthetic control arms |

---

## PopulationSim Skills

Demographics and population health data.

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | PopulationSim master skill |
| `README.md` | Product overview |
| `data-sources.md` | Data source reference |
| `prompt-guide.md` | User prompt guide |
| `developer-guide.md` | Developer documentation |

### Geographic
| Skill | Description |
|-------|-------------|
| `geographic/us-regions.md` | Census regions |
| `geographic/state-patterns.md` | State-level data |
| `geographic/metro-areas.md` | Metropolitan areas |
| `geographic/rural-areas.md` | Rural patterns |
| `geographic/census-tracts.md` | Tract-level analysis |

### Demographics
| Skill | Description |
|-------|-------------|
| `demographics/age-distributions.md` | Age patterns |
| `demographics/gender-patterns.md` | Gender distributions |
| `demographics/race-ethnicity.md` | Race/ethnicity data |
| `demographics/socioeconomic.md` | SES indicators |
| `demographics/household.md` | Household composition |

### Social Determinants
| Skill | Description |
|-------|-------------|
| `sdoh/social-vulnerability.md` | SVI data |
| `sdoh/area-deprivation.md` | ADI data |
| `sdoh/food-access.md` | Food desert data |
| `sdoh/healthcare-access.md` | Access barriers |
| `sdoh/housing.md` | Housing patterns |
| `sdoh/education.md` | Education levels |
| `sdoh/employment.md` | Employment data |

### Health Patterns
| Skill | Description |
|-------|-------------|
| `health-patterns/chronic-disease.md` | Chronic disease prevalence |
| `health-patterns/preventive-care.md` | Screening rates |
| `health-patterns/health-behaviors.md` | Behavioral factors |
| `health-patterns/maternal-child.md` | MCH indicators |
| `health-patterns/mental-health.md` | MH prevalence |
| `health-patterns/health-outcome-disparities.md` | Disparity patterns |
| `health-patterns/health-behavior-patterns.md` | Behavior patterns |

### Population Synthesis
| Skill | Description |
|-------|-------------|
| `synthesis/cohort-design.md` | Cohort specification |
| `synthesis/population-matching.md` | Matching algorithms |
| `synthesis/representative-sampling.md` | Sampling strategies |

---

## NetworkSim Skills

Provider network and facility data.

### Core Skills
| Skill | Description |
|-------|-------------|
| `SKILL.md` | NetworkSim master skill |
| `README.md` | Product overview |
| `prompt-guide.md` | User prompt guide |
| `developer-guide.md` | Developer documentation |

### Query Skills
| Skill | Description |
|-------|-------------|
| `query/provider-search.md` | Provider lookup |
| `query/facility-search.md` | Facility lookup |
| `query/pharmacy-search.md` | Pharmacy lookup |
| `query/npi-validation.md` | NPI validation |
| `query/network-roster.md` | Network rosters |
| `query/provider-density.md` | Provider density analysis |
| `query/coverage-analysis.md` | Coverage analysis |
| `query/physician-quality-search.md` | Physician quality data |
| `query/hospital-quality-search.md` | Hospital quality data |

### Reference Skills
| Skill | Description |
|-------|-------------|
| `reference/network-types.md` | HMO, PPO, EPO, POS |
| `reference/plan-structures.md` | Plan design |
| `reference/network-adequacy.md` | Adequacy standards |
| `reference/pharmacy-benefit-concepts.md` | PBM concepts |
| `reference/pbm-operations.md` | PBM operations |
| `reference/utilization-management.md` | UM programs |
| `reference/specialty-pharmacy.md` | Specialty Rx |

### Network Patterns
| Skill | Description |
|-------|-------------|
| `patterns/hmo-network-pattern.md` | HMO networks |
| `patterns/ppo-network-pattern.md` | PPO networks |
| `patterns/tiered-network-pattern.md` | Tiered networks |
| `patterns/specialty-distribution-pattern.md` | Specialty distribution |
| `patterns/pharmacy-benefit-patterns.md` | Pharmacy networks |

### Synthetic Generation
| Skill | Description |
|-------|-------------|
| `synthetic/synthetic-provider.md` | Generate providers |
| `synthetic/synthetic-facility.md` | Generate facilities |
| `synthetic/synthetic-pharmacy.md` | Generate pharmacies |
| `synthetic/synthetic-network.md` | Generate networks |
| `synthetic/synthetic-plan.md` | Generate plans |
| `synthetic/synthetic-pharmacy-benefit.md` | Generate PBM |

### Analytics
| Skill | Description |
|-------|-------------|
| `analytics/network-adequacy-analysis.md` | Adequacy analysis |
| `analytics/healthcare-deserts.md` | Desert identification |

### Integration
| Skill | Description |
|-------|-------------|
| `integration/provider-for-encounter.md` | PatientSim integration |
| `integration/network-for-member.md` | MemberSim integration |
| `integration/benefit-for-claim.md` | Claims integration |
| `integration/pharmacy-for-rx.md` | RxMemberSim integration |
| `integration/formulary-for-rx.md` | Formulary integration |

---

## Generation Framework Skills

Core generation patterns and utilities.

### Core Framework
| Skill | Description |
|-------|-------------|
| `core/generation-framework.md` | Framework overview |
| `core/event-types.md` | Event type definitions |
| `core/entity-types.md` | Entity specifications |
| `core/skill-resolution.md` | Skill lookup patterns |

### Profiles
| Skill | Description |
|-------|-------------|
| `profiles/profile-schema.md` | Profile format |
| `profiles/profile-execution.md` | Execution patterns |
| `profiles/built-in-profiles.md` | Default profiles |

### Journeys
| Skill | Description |
|-------|-------------|
| `journeys/journey-schema.md` | Journey format |
| `journeys/step-dependencies.md` | Dependency management |
| `journeys/cross-product.md` | Multi-product flows |

### Validation
| Skill | Description |
|-------|-------------|
| `validation/entity-validation.md` | Entity validation |
| `validation/code-validation.md` | Code system validation |
| `validation/relationship-validation.md` | Relationship checks |

---

## Common Skills

Shared across all products.

| Skill | Description |
|-------|-------------|
| `SKILL.md` | Common master skill |
| `README.md` | Common overview |
| `state-management.md` | State persistence patterns |
| `identity-correlation.md` | Cross-product identity |
| `duckdb-skill.md` | Database patterns |

---

## Using Skills

### In Conversation

```
You: Generate a diabetic patient using the diabetes management skill

Claude: [References skills/patientsim/specialty/diabetes.md]
```

### Skill Search

```
You: Search skills for "cardiology"

Claude: Found 3 matching skills:
1. patientsim/specialty/cardiology.md
2. trialsim/therapeutic-areas/cardiovascular.md
3. membersim/value-based-care.md (cardiac programs)
```

### Skill Statistics

```
You: Show skill statistics

Claude: HealthSim Skills Summary:
- Total: 216 skills
- Products: 8
- Most skills: PopulationSim (52)
- Last indexed: 2024-01-15
```

---

## Related Documentation

- [Skills Overview](README.md) - Introduction to skills
- [Creating Skills](creating-skills.md) - How to create new skills
- [Format Specification](format-specification-v2.md) - Skill file format
- [Tools Reference](../tools-reference.md) - Skill tools

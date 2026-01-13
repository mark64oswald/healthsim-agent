# User Guides

In-depth guides for each HealthSim domain and capability.

---

## Product Domain Guides

| Guide | Description |
|-------|-------------|
| [PatientSim](patientsim-guide.md) | Clinical/EMR data - patients, encounters, diagnoses, medications |
| [MemberSim](membersim-guide.md) | Claims/payer data - members, enrollment, professional & facility claims |
| [RxMemberSim](rxmembersim-guide.md) | Pharmacy/PBM data - prescriptions, pharmacy claims, DUR, formulary |
| [TrialSim](trialsim-guide.md) | Clinical trials - subjects, visits, adverse events, SDTM/ADaM |
| [PopulationSim](populationsim-guide.md) | Demographics & SDOH - real CDC/SVI population data |
| [NetworkSim](networksim-guide.md) | Provider networks - real NPPES data queries, synthetic providers |

---

## Cross-Cutting Guides

| Guide | Description |
|-------|-------------|
| [Cross-Product Guide](cross-product-guide.md) | Multi-domain workflows linking data across products |
| [State Management](state-management-guide.md) | Sessions, cohorts, saving, loading, exporting |

---

## Guide Structure

Each guide follows this pattern:

1. **Overview** - What the domain covers
2. **Quick Start** - Get something working in 2 minutes
3. **Common Scenarios** - Detailed examples with outputs
4. **Domain-Specific Sections** - Key concepts for the product
5. **Output Formats** - Available export formats
6. **Tips & Best Practices** - How to get the best results
7. **Troubleshooting** - Common issues and solutions
8. **Related Resources** - Skills, reference docs, examples

---

## Choosing the Right Guide

### Clinical Data Testing

- Single patients → [PatientSim Guide](patientsim-guide.md)
- Oncology scenarios → [PatientSim Guide](patientsim-guide.md) (oncology section)
- Chronic disease → [PatientSim Guide](patientsim-guide.md) (diabetes, CHF, CKD)
- FHIR/HL7 testing → [PatientSim Guide](patientsim-guide.md)

### Claims System Testing

- Professional claims → [MemberSim Guide](membersim-guide.md)
- Facility claims → [MemberSim Guide](membersim-guide.md)
- X12 EDI testing → [MemberSim Guide](membersim-guide.md)

### PBM/Pharmacy Testing

- Pharmacy claims → [RxMemberSim Guide](rxmembersim-guide.md)
- DUR/drug interactions → [RxMemberSim Guide](rxmembersim-guide.md)
- Specialty pharmacy → [RxMemberSim Guide](rxmembersim-guide.md)
- NCPDP testing → [RxMemberSim Guide](rxmembersim-guide.md)

### Clinical Trial Systems

- SDTM/ADaM testing → [TrialSim Guide](trialsim-guide.md)
- Subject enrollment → [TrialSim Guide](trialsim-guide.md)
- Adverse events → [TrialSim Guide](trialsim-guide.md)
- Protocol design → [TrialSim Guide](trialsim-guide.md)

### Population Analytics

- County health data → [PopulationSim Guide](populationsim-guide.md)
- SDOH analysis → [PopulationSim Guide](populationsim-guide.md)
- Social vulnerability → [PopulationSim Guide](populationsim-guide.md)
- Cohort design → [PopulationSim Guide](populationsim-guide.md)

### Provider Data

- Find real providers → [NetworkSim Guide](networksim-guide.md)
- Network adequacy → [NetworkSim Guide](networksim-guide.md)
- Synthetic providers → [NetworkSim Guide](networksim-guide.md)

### Multi-Domain Workflows

- Patient journeys → [Cross-Product Guide](cross-product-guide.md)
- Linked clinical + claims → [Cross-Product Guide](cross-product-guide.md)
- Trial subjects with history → [Cross-Product Guide](cross-product-guide.md)

### Data Persistence

- Save cohorts → [State Management](state-management-guide.md)
- Query saved data → [State Management](state-management-guide.md)
- Export to CSV/JSON → [State Management](state-management-guide.md)

---

## Next Steps

After reading the guides:

1. **Try the examples** - See [Hello HealthSim](../../hello-healthsim/README.md)
2. **Explore skills** - See [Skills Catalog](../skills/README.md)
3. **Check reference docs** - See [Reference](../reference/README.md)

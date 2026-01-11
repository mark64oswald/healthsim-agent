# User Guides

In-depth guides for each HealthSim domain and capability.

---

## Product Domain Guides

| Guide | Description |
|-------|-------------|
| [PatientSim](patientsim-guide.md) | Clinical/EMR data - patients, encounters, diagnoses, medications |
| [MemberSim](membersim-guide.md) | Claims/payer data - members, enrollment, professional & facility claims |
| [RxMemberSim](rxmembersim-guide.md) | Pharmacy/PBM data - prescriptions, pharmacy claims, DUR |
| [TrialSim](trialsim-guide.md) | Clinical trials - subjects, adverse events, SDTM/ADaM |
| [PopulationSim](populationsim-guide.md) | Demographics & SDOH - real population data |
| [NetworkSim](networksim-guide.md) | Provider networks - real NPPES data, synthetic providers |

---

## Cross-Cutting Guides

| Guide | Description |
|-------|-------------|
| [Cross-Product Guide](cross-product-guide.md) | Generate linked data across multiple domains |
| [State Management](state-management-guide.md) | Sessions, saving, loading cohorts |
| [Analytics Guide](analytics-guide.md) | Star schemas, dimensional data, SQL queries |

---

## Guide Structure

Each guide follows this pattern:

1. **Overview** - What the domain covers
2. **Quick Start** - Get something working in 2 minutes
3. **Common Scenarios** - Detailed examples with outputs
4. **Output Formats** - Available export formats
5. **Tips & Best Practices** - How to get the best results
6. **Related Resources** - Skills, reference docs, examples

---

## Choosing the Right Guide

### Clinical Data Testing

- Single patients → [PatientSim Guide](patientsim-guide.md)
- Oncology scenarios → [PatientSim Guide](patientsim-guide.md) (oncology section)
- FHIR/HL7 testing → [PatientSim Guide](patientsim-guide.md)

### Claims System Testing

- Professional claims → [MemberSim Guide](membersim-guide.md)
- Facility claims → [MemberSim Guide](membersim-guide.md)
- X12 EDI testing → [MemberSim Guide](membersim-guide.md)

### PBM/Pharmacy Testing

- Pharmacy claims → [RxMemberSim Guide](rxmembersim-guide.md)
- DUR/interactions → [RxMemberSim Guide](rxmembersim-guide.md)
- NCPDP testing → [RxMemberSim Guide](rxmembersim-guide.md)

### Clinical Trial Systems

- SDTM/ADaM testing → [TrialSim Guide](trialsim-guide.md)
- Subject enrollment → [TrialSim Guide](trialsim-guide.md)
- Adverse events → [TrialSim Guide](trialsim-guide.md)

### Population Analytics

- County-level data → [PopulationSim Guide](populationsim-guide.md)
- SDOH analysis → [PopulationSim Guide](populationsim-guide.md)
- Cohort planning → [PopulationSim Guide](populationsim-guide.md)

### Provider Data

- Find real providers → [NetworkSim Guide](networksim-guide.md)
- Network adequacy → [NetworkSim Guide](networksim-guide.md)
- Generate synthetic → [NetworkSim Guide](networksim-guide.md)

### Multi-Domain Workflows

- Patient journeys → [Cross-Product Guide](cross-product-guide.md)
- Linked data → [Cross-Product Guide](cross-product-guide.md)

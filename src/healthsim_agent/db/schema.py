"""
Database schema definitions for HealthSim Agent.

Defines DDL for canonical tables, state management tables,
and system tables for the standalone agent application.

Ported from: healthsim-workspace/packages/core/src/healthsim/db/schema.py
"""

from typing import List

# Current schema version
SCHEMA_VERSION = "1.0"

# Standard provenance columns included in all canonical tables
PROVENANCE_COLUMNS = """
    cohort_id           VARCHAR,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_type         VARCHAR,
    source_system       VARCHAR,
    skill_used          VARCHAR,
    generation_seed     INTEGER
"""

# ============================================================================
# SYSTEM TABLES
# ============================================================================

SCHEMA_MIGRATIONS_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version         VARCHAR PRIMARY KEY,
    description     VARCHAR,
    applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ============================================================================
# STATE MANAGEMENT TABLES
# ============================================================================

COHORT_ENTITIES_SEQ_DDL = """
CREATE SEQUENCE IF NOT EXISTS cohort_entities_seq START 1;
"""

COHORT_TAGS_SEQ_DDL = """
CREATE SEQUENCE IF NOT EXISTS cohort_tags_seq START 1;
"""

COHORTS_DDL = """
CREATE TABLE IF NOT EXISTS cohorts (
    id              VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL UNIQUE,
    description     VARCHAR,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata        JSON
);
"""

COHORT_ENTITIES_DDL = """
CREATE TABLE IF NOT EXISTS cohort_entities (
    id              INTEGER PRIMARY KEY DEFAULT nextval('cohort_entities_seq'),
    cohort_id       VARCHAR NOT NULL REFERENCES cohorts(id),
    entity_type     VARCHAR NOT NULL,
    entity_id       VARCHAR NOT NULL,
    entity_data     JSON,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cohort_id, entity_type, entity_id)
);
"""

COHORT_TAGS_DDL = """
CREATE TABLE IF NOT EXISTS cohort_tags (
    id              INTEGER PRIMARY KEY DEFAULT nextval('cohort_tags_seq'),
    cohort_id       VARCHAR NOT NULL REFERENCES cohorts(id),
    tag             VARCHAR NOT NULL,
    UNIQUE(cohort_id, tag)
);
"""

# ============================================================================
# CANONICAL TABLES - PatientSim
# ============================================================================

PATIENTS_DDL = f"""
CREATE TABLE IF NOT EXISTS patients (
    id              VARCHAR PRIMARY KEY,
    mrn             VARCHAR NOT NULL,
    ssn             VARCHAR,
    given_name      VARCHAR NOT NULL,
    middle_name     VARCHAR,
    family_name     VARCHAR NOT NULL,
    suffix          VARCHAR,
    prefix          VARCHAR,
    birth_date      DATE NOT NULL,
    gender          VARCHAR NOT NULL,
    race            VARCHAR,
    ethnicity       VARCHAR,
    language        VARCHAR DEFAULT 'en',
    street_address  VARCHAR,
    street_address_2 VARCHAR,
    city            VARCHAR,
    state           VARCHAR,
    postal_code     VARCHAR,
    country         VARCHAR DEFAULT 'US',
    phone           VARCHAR,
    phone_mobile    VARCHAR,
    email           VARCHAR,
    deceased        BOOLEAN DEFAULT FALSE,
    death_date      DATE,
    {PROVENANCE_COLUMNS}
);
"""

ENCOUNTERS_DDL = f"""
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id    VARCHAR PRIMARY KEY,
    patient_mrn     VARCHAR NOT NULL,
    class_code      VARCHAR NOT NULL,
    status          VARCHAR NOT NULL,
    admission_time  TIMESTAMP NOT NULL,
    discharge_time  TIMESTAMP,
    facility        VARCHAR,
    department      VARCHAR,
    room            VARCHAR,
    bed             VARCHAR,
    chief_complaint VARCHAR,
    admitting_diagnosis VARCHAR,
    discharge_disposition VARCHAR,
    attending_physician VARCHAR,
    admitting_physician VARCHAR,
    {PROVENANCE_COLUMNS}
);
"""

DIAGNOSES_DDL = f"""
CREATE TABLE IF NOT EXISTS diagnoses (
    id              VARCHAR PRIMARY KEY,
    code            VARCHAR NOT NULL,
    description     VARCHAR,
    type            VARCHAR DEFAULT 'final',
    patient_mrn     VARCHAR NOT NULL,
    encounter_id    VARCHAR,
    diagnosed_date  DATE NOT NULL,
    resolved_date   DATE,
    {PROVENANCE_COLUMNS}
);
"""

MEDICATIONS_DDL = f"""
CREATE TABLE IF NOT EXISTS medications (
    id              VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL,
    code            VARCHAR,
    dose            VARCHAR NOT NULL,
    route           VARCHAR NOT NULL,
    frequency       VARCHAR NOT NULL,
    patient_mrn     VARCHAR NOT NULL,
    encounter_id    VARCHAR,
    start_date      TIMESTAMP NOT NULL,
    end_date        TIMESTAMP,
    status          VARCHAR DEFAULT 'active',
    prescriber      VARCHAR,
    indication      VARCHAR,
    {PROVENANCE_COLUMNS}
);
"""

LAB_RESULTS_DDL = f"""
CREATE TABLE IF NOT EXISTS lab_results (
    id              VARCHAR PRIMARY KEY,
    test_name       VARCHAR NOT NULL,
    loinc_code      VARCHAR,
    value           VARCHAR NOT NULL,
    unit            VARCHAR,
    reference_range VARCHAR,
    abnormal_flag   VARCHAR,
    patient_mrn     VARCHAR NOT NULL,
    encounter_id    VARCHAR,
    collected_time  TIMESTAMP NOT NULL,
    resulted_time   TIMESTAMP,
    performing_lab  VARCHAR,
    ordering_provider VARCHAR,
    {PROVENANCE_COLUMNS}
);
"""

# ============================================================================
# CANONICAL TABLES - MemberSim
# ============================================================================

MEMBERS_DDL = f"""
CREATE TABLE IF NOT EXISTS members (
    id              VARCHAR PRIMARY KEY,
    member_id       VARCHAR NOT NULL,
    subscriber_id   VARCHAR,
    relationship_code VARCHAR DEFAULT '18',
    ssn             VARCHAR,
    given_name      VARCHAR NOT NULL,
    middle_name     VARCHAR,
    family_name     VARCHAR NOT NULL,
    birth_date      DATE NOT NULL,
    gender          VARCHAR NOT NULL,
    street_address  VARCHAR,
    city            VARCHAR,
    state           VARCHAR,
    postal_code     VARCHAR,
    phone           VARCHAR,
    email           VARCHAR,
    group_id        VARCHAR NOT NULL,
    plan_code       VARCHAR NOT NULL,
    coverage_start  DATE NOT NULL,
    coverage_end    DATE,
    pcp_npi         VARCHAR,
    {PROVENANCE_COLUMNS}
);
"""

CLAIMS_DDL = f"""
CREATE TABLE IF NOT EXISTS claims (
    claim_id        VARCHAR PRIMARY KEY,
    claim_type      VARCHAR NOT NULL,
    member_id       VARCHAR NOT NULL,
    subscriber_id   VARCHAR,
    provider_npi    VARCHAR NOT NULL,
    facility_npi    VARCHAR,
    service_date    DATE NOT NULL,
    admission_date  DATE,
    discharge_date  DATE,
    place_of_service VARCHAR DEFAULT '11',
    principal_diagnosis VARCHAR NOT NULL,
    other_diagnoses JSON,
    authorization_number VARCHAR,
    total_charge    DECIMAL(12,2),
    total_allowed   DECIMAL(12,2),
    total_paid      DECIMAL(12,2),
    member_responsibility DECIMAL(12,2),
    {PROVENANCE_COLUMNS}
);
"""

CLAIM_LINES_DDL = f"""
CREATE TABLE IF NOT EXISTS claim_lines (
    id              VARCHAR PRIMARY KEY,
    claim_id        VARCHAR NOT NULL,
    line_number     INTEGER NOT NULL,
    procedure_code  VARCHAR NOT NULL,
    procedure_modifiers JSON,
    service_date    DATE NOT NULL,
    units           DECIMAL(6,2) DEFAULT 1,
    charge_amount   DECIMAL(12,2) NOT NULL,
    allowed_amount  DECIMAL(12,2),
    paid_amount     DECIMAL(12,2),
    diagnosis_pointers JSON,
    revenue_code    VARCHAR,
    ndc_code        VARCHAR,
    place_of_service VARCHAR DEFAULT '11',
    {PROVENANCE_COLUMNS}
);
"""

# ============================================================================
# CANONICAL TABLES - RxMemberSim
# ============================================================================

PRESCRIPTIONS_DDL = f"""
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_number VARCHAR PRIMARY KEY,
    patient_mrn     VARCHAR,
    member_id       VARCHAR,
    ndc             VARCHAR NOT NULL,
    drug_name       VARCHAR NOT NULL,
    quantity_prescribed DECIMAL(10,2) NOT NULL,
    days_supply     INTEGER NOT NULL,
    refills_authorized INTEGER DEFAULT 0,
    refills_remaining INTEGER DEFAULT 0,
    prescriber_npi  VARCHAR NOT NULL,
    prescriber_name VARCHAR,
    prescriber_dea  VARCHAR,
    written_date    DATE NOT NULL,
    expiration_date DATE NOT NULL,
    daw_code        VARCHAR DEFAULT '0',
    directions      TEXT,
    {PROVENANCE_COLUMNS}
);
"""

PHARMACY_CLAIMS_DDL = f"""
CREATE TABLE IF NOT EXISTS pharmacy_claims (
    claim_id        VARCHAR PRIMARY KEY,
    transaction_code VARCHAR NOT NULL,
    service_date    DATE NOT NULL,
    pharmacy_npi    VARCHAR NOT NULL,
    pharmacy_ncpdp  VARCHAR,
    member_id       VARCHAR NOT NULL,
    cardholder_id   VARCHAR NOT NULL,
    person_code     VARCHAR,
    bin             VARCHAR NOT NULL,
    pcn             VARCHAR NOT NULL,
    group_number    VARCHAR NOT NULL,
    prescription_number VARCHAR NOT NULL,
    fill_number     INTEGER DEFAULT 0,
    ndc             VARCHAR NOT NULL,
    quantity_dispensed DECIMAL(10,2) NOT NULL,
    days_supply     INTEGER NOT NULL,
    daw_code        VARCHAR,
    prescriber_npi  VARCHAR NOT NULL,
    ingredient_cost_submitted DECIMAL(12,2),
    dispensing_fee_submitted DECIMAL(12,2),
    usual_customary_charge DECIMAL(12,2),
    gross_amount_due DECIMAL(12,2),
    patient_pay_amount DECIMAL(12,2),
    {PROVENANCE_COLUMNS}
);
"""

# ============================================================================
# CANONICAL TABLES - TrialSim
# ============================================================================

SUBJECTS_DDL = f"""
CREATE TABLE IF NOT EXISTS subjects (
    id              VARCHAR PRIMARY KEY,
    subject_id      VARCHAR NOT NULL,
    usubjid         VARCHAR NOT NULL,
    study_id        VARCHAR NOT NULL,
    site_id         VARCHAR NOT NULL,
    patient_ref     VARCHAR,
    ssn             VARCHAR,
    given_name      VARCHAR NOT NULL,
    family_name     VARCHAR NOT NULL,
    birth_date      DATE NOT NULL,
    gender          VARCHAR NOT NULL,
    race            VARCHAR,
    ethnicity       VARCHAR,
    screening_id    VARCHAR,
    screening_date  DATE,
    informed_consent_date DATE NOT NULL,
    randomization_date DATE,
    treatment_arm   VARCHAR,
    status          VARCHAR NOT NULL,
    {PROVENANCE_COLUMNS}
);
"""

ADVERSE_EVENTS_DDL = f"""
CREATE TABLE IF NOT EXISTS adverse_events (
    id              VARCHAR PRIMARY KEY,
    usubjid         VARCHAR NOT NULL,
    aeseq           INTEGER,
    aeterm          VARCHAR NOT NULL,
    aedecod         VARCHAR,
    aebodsys        VARCHAR,
    aestdtc         DATE NOT NULL,
    aeendtc         DATE,
    aesev           VARCHAR,
    aetoxgr         VARCHAR,
    aeser           VARCHAR,
    aerel           VARCHAR,
    aeacn           VARCHAR,
    aeout           VARCHAR,
    {PROVENANCE_COLUMNS}
);
"""

# ============================================================================
# INDEXES
# ============================================================================

INDEXES_DDL = """
-- Patient lookups
CREATE INDEX IF NOT EXISTS idx_patients_ssn ON patients(ssn);
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(mrn);
CREATE INDEX IF NOT EXISTS idx_patients_cohort ON patients(cohort_id);

-- Encounter lookups
CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_mrn);
CREATE INDEX IF NOT EXISTS idx_encounters_cohort ON encounters(cohort_id);

-- Member lookups
CREATE INDEX IF NOT EXISTS idx_members_ssn ON members(ssn);
CREATE INDEX IF NOT EXISTS idx_members_cohort ON members(cohort_id);

-- Claim lookups
CREATE INDEX IF NOT EXISTS idx_claims_member ON claims(member_id);
CREATE INDEX IF NOT EXISTS idx_claims_cohort ON claims(cohort_id);

-- Subject lookups
CREATE INDEX IF NOT EXISTS idx_subjects_study ON subjects(study_id);
CREATE INDEX IF NOT EXISTS idx_subjects_cohort ON subjects(cohort_id);

-- Cohort entity lookups
CREATE INDEX IF NOT EXISTS idx_cohort_entities_cohort ON cohort_entities(cohort_id);
CREATE INDEX IF NOT EXISTS idx_cohort_entities_type ON cohort_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_cohort_tags_cohort ON cohort_tags(cohort_id);
"""

# ============================================================================
# ALL DDL IN ORDER
# ============================================================================

ALL_DDL = [
    SCHEMA_MIGRATIONS_DDL,
    COHORT_ENTITIES_SEQ_DDL,
    COHORT_TAGS_SEQ_DDL,
    COHORTS_DDL,
    COHORT_ENTITIES_DDL,
    COHORT_TAGS_DDL,
    PATIENTS_DDL,
    ENCOUNTERS_DDL,
    DIAGNOSES_DDL,
    MEDICATIONS_DDL,
    LAB_RESULTS_DDL,
    MEMBERS_DDL,
    CLAIMS_DDL,
    CLAIM_LINES_DDL,
    PRESCRIPTIONS_DDL,
    PHARMACY_CLAIMS_DDL,
    SUBJECTS_DDL,
    ADVERSE_EVENTS_DDL,
    INDEXES_DDL,
]


def get_canonical_tables() -> List[str]:
    """Get list of canonical table names."""
    return [
        'patients', 'encounters', 'diagnoses', 'medications', 'lab_results',
        'members', 'claims', 'claim_lines',
        'prescriptions', 'pharmacy_claims',
        'subjects', 'adverse_events'
    ]


def get_state_tables() -> List[str]:
    """Get list of state management table names."""
    return ['cohorts', 'cohort_entities', 'cohort_tags']


def get_system_tables() -> List[str]:
    """Get list of system table names."""
    return ['schema_migrations']

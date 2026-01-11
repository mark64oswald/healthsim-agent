"""Reference data for TrialSim.

Contains:
- MedDRA coding for adverse events
- Lab test reference ranges and LOINC codes
- Therapeutic areas and indications
- Common concomitant medications
- Standard vital signs reference ranges
"""

from typing import Any


# =============================================================================
# MedDRA Reference Data (Simplified for synthetic data)
# =============================================================================

MEDDRA_ADVERSE_EVENTS: list[dict[str, Any]] = [
    # Gastrointestinal disorders (SOC code: 10017947)
    {"pt_code": "10028813", "pt_name": "Nausea", "soc_code": "10017947", "soc_name": "Gastrointestinal disorders", "llt_code": "10028813"},
    {"pt_code": "10012735", "pt_name": "Diarrhea", "soc_code": "10017947", "soc_name": "Gastrointestinal disorders", "llt_code": "10012735"},
    {"pt_code": "10047700", "pt_name": "Vomiting", "soc_code": "10017947", "soc_name": "Gastrointestinal disorders", "llt_code": "10047700"},
    {"pt_code": "10000081", "pt_name": "Abdominal pain", "soc_code": "10017947", "soc_name": "Gastrointestinal disorders", "llt_code": "10000081"},
    {"pt_code": "10010774", "pt_name": "Constipation", "soc_code": "10017947", "soc_name": "Gastrointestinal disorders", "llt_code": "10010774"},
    
    # Nervous system disorders (SOC code: 10029205)
    {"pt_code": "10019211", "pt_name": "Headache", "soc_code": "10029205", "soc_name": "Nervous system disorders", "llt_code": "10019211"},
    {"pt_code": "10013573", "pt_name": "Dizziness", "soc_code": "10029205", "soc_name": "Nervous system disorders", "llt_code": "10013573"},
    {"pt_code": "10041349", "pt_name": "Somnolence", "soc_code": "10029205", "soc_name": "Nervous system disorders", "llt_code": "10041349"},
    {"pt_code": "10043458", "pt_name": "Tremor", "soc_code": "10029205", "soc_name": "Nervous system disorders", "llt_code": "10043458"},
    {"pt_code": "10033775", "pt_name": "Paraesthesia", "soc_code": "10029205", "soc_name": "Nervous system disorders", "llt_code": "10033775"},
    
    # General disorders (SOC code: 10018065)
    {"pt_code": "10016256", "pt_name": "Fatigue", "soc_code": "10018065", "soc_name": "General disorders and administration site conditions", "llt_code": "10016256"},
    {"pt_code": "10003549", "pt_name": "Asthenia", "soc_code": "10018065", "soc_name": "General disorders and administration site conditions", "llt_code": "10003549"},
    {"pt_code": "10030124", "pt_name": "Oedema peripheral", "soc_code": "10018065", "soc_name": "General disorders and administration site conditions", "llt_code": "10030124"},
    {"pt_code": "10037660", "pt_name": "Pyrexia", "soc_code": "10018065", "soc_name": "General disorders and administration site conditions", "llt_code": "10037660"},
    
    # Skin and subcutaneous tissue disorders (SOC code: 10040785)
    {"pt_code": "10037844", "pt_name": "Rash", "soc_code": "10040785", "soc_name": "Skin and subcutaneous tissue disorders", "llt_code": "10037844"},
    {"pt_code": "10037087", "pt_name": "Pruritus", "soc_code": "10040785", "soc_name": "Skin and subcutaneous tissue disorders", "llt_code": "10037087"},
    {"pt_code": "10001760", "pt_name": "Alopecia", "soc_code": "10040785", "soc_name": "Skin and subcutaneous tissue disorders", "llt_code": "10001760"},
    {"pt_code": "10013786", "pt_name": "Dry skin", "soc_code": "10040785", "soc_name": "Skin and subcutaneous tissue disorders", "llt_code": "10013786"},
    
    # Musculoskeletal disorders (SOC code: 10028395)
    {"pt_code": "10003239", "pt_name": "Arthralgia", "soc_code": "10028395", "soc_name": "Musculoskeletal and connective tissue disorders", "llt_code": "10003239"},
    {"pt_code": "10028411", "pt_name": "Myalgia", "soc_code": "10028395", "soc_name": "Musculoskeletal and connective tissue disorders", "llt_code": "10028411"},
    {"pt_code": "10003988", "pt_name": "Back pain", "soc_code": "10028395", "soc_name": "Musculoskeletal and connective tissue disorders", "llt_code": "10003988"},
    
    # Respiratory disorders (SOC code: 10038738)
    {"pt_code": "10011224", "pt_name": "Cough", "soc_code": "10038738", "soc_name": "Respiratory, thoracic and mediastinal disorders", "llt_code": "10011224"},
    {"pt_code": "10013968", "pt_name": "Dyspnoea", "soc_code": "10038738", "soc_name": "Respiratory, thoracic and mediastinal disorders", "llt_code": "10013968"},
    {"pt_code": "10028735", "pt_name": "Nasopharyngitis", "soc_code": "10038738", "soc_name": "Respiratory, thoracic and mediastinal disorders", "llt_code": "10028735"},
    
    # Psychiatric disorders (SOC code: 10037175)
    {"pt_code": "10022437", "pt_name": "Insomnia", "soc_code": "10037175", "soc_name": "Psychiatric disorders", "llt_code": "10022437"},
    {"pt_code": "10002855", "pt_name": "Anxiety", "soc_code": "10037175", "soc_name": "Psychiatric disorders", "llt_code": "10002855"},
    {"pt_code": "10012378", "pt_name": "Depression", "soc_code": "10037175", "soc_name": "Psychiatric disorders", "llt_code": "10012378"},
]


# =============================================================================
# Laboratory Test Reference Data
# =============================================================================

LAB_TESTS: list[dict[str, Any]] = [
    # Hematology
    {"test": "HGB", "name": "Hemoglobin", "category": "hematology", "unit": "g/dL", "low_m": 13.5, "high_m": 17.5, "low_f": 12.0, "high_f": 16.0, "loinc": "718-7", "specimen": "BLOOD"},
    {"test": "HCT", "name": "Hematocrit", "category": "hematology", "unit": "%", "low_m": 38.8, "high_m": 50.0, "low_f": 34.9, "high_f": 44.5, "loinc": "4544-3", "specimen": "BLOOD"},
    {"test": "WBC", "name": "White Blood Cell Count", "category": "hematology", "unit": "10^9/L", "low": 4.5, "high": 11.0, "loinc": "6690-2", "specimen": "BLOOD"},
    {"test": "PLT", "name": "Platelet Count", "category": "hematology", "unit": "10^9/L", "low": 150, "high": 400, "loinc": "777-3", "specimen": "BLOOD"},
    {"test": "RBC", "name": "Red Blood Cell Count", "category": "hematology", "unit": "10^12/L", "low_m": 4.5, "high_m": 5.9, "low_f": 4.1, "high_f": 5.1, "loinc": "789-8", "specimen": "BLOOD"},
    {"test": "NEUT", "name": "Neutrophils", "category": "hematology", "unit": "%", "low": 40, "high": 70, "loinc": "770-8", "specimen": "BLOOD"},
    {"test": "LYMPH", "name": "Lymphocytes", "category": "hematology", "unit": "%", "low": 20, "high": 40, "loinc": "736-9", "specimen": "BLOOD"},
    
    # Chemistry - Liver
    {"test": "ALT", "name": "Alanine Aminotransferase", "category": "chemistry", "unit": "U/L", "low": 7, "high": 56, "loinc": "1742-6", "specimen": "SERUM"},
    {"test": "AST", "name": "Aspartate Aminotransferase", "category": "chemistry", "unit": "U/L", "low": 10, "high": 40, "loinc": "1920-8", "specimen": "SERUM"},
    {"test": "ALP", "name": "Alkaline Phosphatase", "category": "chemistry", "unit": "U/L", "low": 44, "high": 147, "loinc": "6768-6", "specimen": "SERUM"},
    {"test": "TBIL", "name": "Total Bilirubin", "category": "chemistry", "unit": "mg/dL", "low": 0.1, "high": 1.2, "loinc": "1975-2", "specimen": "SERUM"},
    {"test": "ALB", "name": "Albumin", "category": "chemistry", "unit": "g/dL", "low": 3.4, "high": 5.4, "loinc": "1751-7", "specimen": "SERUM"},
    
    # Chemistry - Kidney
    {"test": "CREAT", "name": "Creatinine", "category": "chemistry", "unit": "mg/dL", "low_m": 0.74, "high_m": 1.35, "low_f": 0.59, "high_f": 1.04, "loinc": "2160-0", "specimen": "SERUM"},
    {"test": "BUN", "name": "Blood Urea Nitrogen", "category": "chemistry", "unit": "mg/dL", "low": 7, "high": 20, "loinc": "3094-0", "specimen": "SERUM"},
    {"test": "EGFR", "name": "Estimated GFR", "category": "chemistry", "unit": "mL/min/1.73m2", "low": 60, "high": 999, "loinc": "33914-3", "specimen": "SERUM"},
    
    # Chemistry - Electrolytes
    {"test": "NA", "name": "Sodium", "category": "chemistry", "unit": "mmol/L", "low": 136, "high": 145, "loinc": "2951-2", "specimen": "SERUM"},
    {"test": "K", "name": "Potassium", "category": "chemistry", "unit": "mmol/L", "low": 3.5, "high": 5.0, "loinc": "2823-3", "specimen": "SERUM"},
    {"test": "CL", "name": "Chloride", "category": "chemistry", "unit": "mmol/L", "low": 98, "high": 106, "loinc": "2075-0", "specimen": "SERUM"},
    {"test": "CO2", "name": "Carbon Dioxide", "category": "chemistry", "unit": "mmol/L", "low": 23, "high": 29, "loinc": "2028-9", "specimen": "SERUM"},
    {"test": "CA", "name": "Calcium", "category": "chemistry", "unit": "mg/dL", "low": 8.6, "high": 10.2, "loinc": "17861-6", "specimen": "SERUM"},
    {"test": "MG", "name": "Magnesium", "category": "chemistry", "unit": "mg/dL", "low": 1.7, "high": 2.2, "loinc": "19123-9", "specimen": "SERUM"},
    {"test": "PHOS", "name": "Phosphorus", "category": "chemistry", "unit": "mg/dL", "low": 2.5, "high": 4.5, "loinc": "2777-1", "specimen": "SERUM"},
    
    # Chemistry - Metabolic
    {"test": "GLUC", "name": "Glucose", "category": "chemistry", "unit": "mg/dL", "low": 70, "high": 100, "loinc": "2345-7", "specimen": "SERUM"},
    {"test": "HBA1C", "name": "Hemoglobin A1c", "category": "chemistry", "unit": "%", "low": 4.0, "high": 5.6, "loinc": "4548-4", "specimen": "BLOOD"},
    {"test": "CHOL", "name": "Total Cholesterol", "category": "chemistry", "unit": "mg/dL", "low": 0, "high": 200, "loinc": "2093-3", "specimen": "SERUM"},
    {"test": "LDL", "name": "LDL Cholesterol", "category": "chemistry", "unit": "mg/dL", "low": 0, "high": 100, "loinc": "13457-7", "specimen": "SERUM"},
    {"test": "HDL", "name": "HDL Cholesterol", "category": "chemistry", "unit": "mg/dL", "low": 40, "high": 999, "loinc": "2085-9", "specimen": "SERUM"},
    {"test": "TRIG", "name": "Triglycerides", "category": "chemistry", "unit": "mg/dL", "low": 0, "high": 150, "loinc": "2571-8", "specimen": "SERUM"},
    
    # Coagulation
    {"test": "PT", "name": "Prothrombin Time", "category": "coagulation", "unit": "sec", "low": 11.0, "high": 13.5, "loinc": "5902-2", "specimen": "PLASMA"},
    {"test": "INR", "name": "INR", "category": "coagulation", "unit": "ratio", "low": 0.8, "high": 1.1, "loinc": "6301-6", "specimen": "PLASMA"},
    {"test": "APTT", "name": "Activated PTT", "category": "coagulation", "unit": "sec", "low": 25, "high": 35, "loinc": "3173-2", "specimen": "PLASMA"},
]


# =============================================================================
# Vital Signs Reference Data
# =============================================================================

VITAL_SIGNS: list[dict[str, Any]] = [
    {"test": "SYSBP", "name": "Systolic Blood Pressure", "unit": "mmHg", "low": 90, "high": 120, "position": "SITTING"},
    {"test": "DIABP", "name": "Diastolic Blood Pressure", "unit": "mmHg", "low": 60, "high": 80, "position": "SITTING"},
    {"test": "PULSE", "name": "Heart Rate", "unit": "beats/min", "low": 60, "high": 100, "position": "SITTING"},
    {"test": "RESP", "name": "Respiratory Rate", "unit": "breaths/min", "low": 12, "high": 20, "position": "SITTING"},
    {"test": "TEMP", "name": "Body Temperature", "unit": "C", "low": 36.1, "high": 37.2, "position": None},
    {"test": "WEIGHT", "name": "Weight", "unit": "kg", "low": 40, "high": 150, "position": "STANDING"},
    {"test": "HEIGHT", "name": "Height", "unit": "cm", "low": 140, "high": 200, "position": "STANDING"},
    {"test": "BMI", "name": "Body Mass Index", "unit": "kg/m2", "low": 18.5, "high": 24.9, "position": None},
    {"test": "OXYSAT", "name": "Oxygen Saturation", "unit": "%", "low": 95, "high": 100, "position": "SITTING"},
]


# =============================================================================
# Therapeutic Areas and Indications
# =============================================================================

THERAPEUTIC_AREAS: dict[str, list[str]] = {
    "Oncology": [
        "Non-Small Cell Lung Cancer",
        "Breast Cancer",
        "Colorectal Cancer",
        "Melanoma",
        "Renal Cell Carcinoma",
        "Hepatocellular Carcinoma",
        "Multiple Myeloma",
        "Chronic Lymphocytic Leukemia",
        "Prostate Cancer",
        "Ovarian Cancer",
    ],
    "Cardiovascular": [
        "Hypertension",
        "Heart Failure",
        "Atrial Fibrillation",
        "Acute Coronary Syndrome",
        "Peripheral Artery Disease",
        "Hyperlipidemia",
        "Pulmonary Arterial Hypertension",
    ],
    "Neurology": [
        "Alzheimer's Disease",
        "Parkinson's Disease",
        "Multiple Sclerosis",
        "Epilepsy",
        "Migraine",
        "Amyotrophic Lateral Sclerosis",
        "Huntington's Disease",
    ],
    "Immunology": [
        "Rheumatoid Arthritis",
        "Psoriasis",
        "Systemic Lupus Erythematosus",
        "Crohn's Disease",
        "Ulcerative Colitis",
        "Atopic Dermatitis",
        "Ankylosing Spondylitis",
    ],
    "Infectious Disease": [
        "HIV/AIDS",
        "Hepatitis C",
        "Hepatitis B",
        "COVID-19",
        "Influenza",
        "Bacterial Pneumonia",
        "Tuberculosis",
    ],
    "Endocrinology": [
        "Type 2 Diabetes",
        "Type 1 Diabetes",
        "Obesity",
        "Hypothyroidism",
        "Growth Hormone Deficiency",
        "Hypoparathyroidism",
    ],
    "Respiratory": [
        "Asthma",
        "COPD",
        "Idiopathic Pulmonary Fibrosis",
        "Cystic Fibrosis",
        "Pulmonary Embolism",
    ],
    "Rare Disease": [
        "Duchenne Muscular Dystrophy",
        "Spinal Muscular Atrophy",
        "Hemophilia A",
        "Hemophilia B",
        "Fabry Disease",
        "Gaucher Disease",
        "Hereditary Angioedema",
    ],
}


# =============================================================================
# Common Concomitant Medications (with ATC codes)
# =============================================================================

CONCOMITANT_MEDICATIONS: list[dict[str, Any]] = [
    # Analgesics
    {"drug": "Acetaminophen", "class": "Analgesic", "atc": "N02BE01", "dose": 500, "unit": "mg", "route": "oral", "frequency": "Q6H PRN"},
    {"drug": "Ibuprofen", "class": "NSAID", "atc": "M01AE01", "dose": 400, "unit": "mg", "route": "oral", "frequency": "TID"},
    {"drug": "Aspirin", "class": "Analgesic/Antiplatelet", "atc": "B01AC06", "dose": 81, "unit": "mg", "route": "oral", "frequency": "QD"},
    
    # Cardiovascular
    {"drug": "Lisinopril", "class": "ACE Inhibitor", "atc": "C09AA03", "dose": 10, "unit": "mg", "route": "oral", "frequency": "QD"},
    {"drug": "Metoprolol", "class": "Beta Blocker", "atc": "C07AB02", "dose": 50, "unit": "mg", "route": "oral", "frequency": "BID"},
    {"drug": "Amlodipine", "class": "Calcium Channel Blocker", "atc": "C08CA01", "dose": 5, "unit": "mg", "route": "oral", "frequency": "QD"},
    {"drug": "Atorvastatin", "class": "Statin", "atc": "C10AA05", "dose": 20, "unit": "mg", "route": "oral", "frequency": "QD"},
    {"drug": "Hydrochlorothiazide", "class": "Diuretic", "atc": "C03AA03", "dose": 25, "unit": "mg", "route": "oral", "frequency": "QD"},
    
    # Gastrointestinal
    {"drug": "Omeprazole", "class": "PPI", "atc": "A02BC01", "dose": 20, "unit": "mg", "route": "oral", "frequency": "QD"},
    {"drug": "Ondansetron", "class": "Antiemetic", "atc": "A04AA01", "dose": 8, "unit": "mg", "route": "oral", "frequency": "Q8H PRN"},
    
    # Diabetes
    {"drug": "Metformin", "class": "Biguanide", "atc": "A10BA02", "dose": 500, "unit": "mg", "route": "oral", "frequency": "BID"},
    {"drug": "Glipizide", "class": "Sulfonylurea", "atc": "A10BB07", "dose": 5, "unit": "mg", "route": "oral", "frequency": "QD"},
    
    # Thyroid
    {"drug": "Levothyroxine", "class": "Thyroid Hormone", "atc": "H03AA01", "dose": 75, "unit": "mcg", "route": "oral", "frequency": "QD"},
    
    # Psychiatric
    {"drug": "Sertraline", "class": "SSRI", "atc": "N06AB06", "dose": 50, "unit": "mg", "route": "oral", "frequency": "QD"},
    {"drug": "Alprazolam", "class": "Benzodiazepine", "atc": "N05BA12", "dose": 0.5, "unit": "mg", "route": "oral", "frequency": "PRN"},
    
    # Supplements
    {"drug": "Vitamin D", "class": "Vitamin", "atc": "A11CC05", "dose": 1000, "unit": "IU", "route": "oral", "frequency": "QD"},
    {"drug": "Calcium Carbonate", "class": "Mineral Supplement", "atc": "A12AA04", "dose": 500, "unit": "mg", "route": "oral", "frequency": "BID"},
    {"drug": "Multivitamin", "class": "Vitamin", "atc": "A11AA03", "dose": 1, "unit": "tablet", "route": "oral", "frequency": "QD"},
]


# =============================================================================
# Common Medical History Items
# =============================================================================

MEDICAL_HISTORY_ITEMS: list[dict[str, Any]] = [
    # Cardiovascular
    {"term": "Hypertension", "category": "CARDIOVASCULAR", "meddra_pt": "10020772", "soc": "Vascular disorders"},
    {"term": "Hyperlipidemia", "category": "CARDIOVASCULAR", "meddra_pt": "10020870", "soc": "Metabolism and nutrition disorders"},
    {"term": "Coronary Artery Disease", "category": "CARDIOVASCULAR", "meddra_pt": "10011089", "soc": "Cardiac disorders"},
    {"term": "Atrial Fibrillation", "category": "CARDIOVASCULAR", "meddra_pt": "10003658", "soc": "Cardiac disorders"},
    
    # Metabolic
    {"term": "Type 2 Diabetes Mellitus", "category": "METABOLIC", "meddra_pt": "10067585", "soc": "Metabolism and nutrition disorders"},
    {"term": "Obesity", "category": "METABOLIC", "meddra_pt": "10029883", "soc": "Metabolism and nutrition disorders"},
    {"term": "Hypothyroidism", "category": "METABOLIC", "meddra_pt": "10021114", "soc": "Endocrine disorders"},
    
    # Respiratory
    {"term": "Asthma", "category": "RESPIRATORY", "meddra_pt": "10003553", "soc": "Respiratory, thoracic and mediastinal disorders"},
    {"term": "COPD", "category": "RESPIRATORY", "meddra_pt": "10009033", "soc": "Respiratory, thoracic and mediastinal disorders"},
    
    # Gastrointestinal
    {"term": "GERD", "category": "GASTROINTESTINAL", "meddra_pt": "10017885", "soc": "Gastrointestinal disorders"},
    {"term": "Peptic Ulcer Disease", "category": "GASTROINTESTINAL", "meddra_pt": "10034341", "soc": "Gastrointestinal disorders"},
    
    # Musculoskeletal
    {"term": "Osteoarthritis", "category": "MUSCULOSKELETAL", "meddra_pt": "10031161", "soc": "Musculoskeletal and connective tissue disorders"},
    {"term": "Osteoporosis", "category": "MUSCULOSKELETAL", "meddra_pt": "10031282", "soc": "Musculoskeletal and connective tissue disorders"},
    {"term": "Back Pain", "category": "MUSCULOSKELETAL", "meddra_pt": "10003988", "soc": "Musculoskeletal and connective tissue disorders"},
    
    # Psychiatric
    {"term": "Depression", "category": "PSYCHIATRIC", "meddra_pt": "10012378", "soc": "Psychiatric disorders"},
    {"term": "Anxiety Disorder", "category": "PSYCHIATRIC", "meddra_pt": "10002855", "soc": "Psychiatric disorders"},
    {"term": "Insomnia", "category": "PSYCHIATRIC", "meddra_pt": "10022437", "soc": "Psychiatric disorders"},
    
    # Neurological
    {"term": "Migraine", "category": "NEUROLOGICAL", "meddra_pt": "10027599", "soc": "Nervous system disorders"},
    {"term": "Peripheral Neuropathy", "category": "NEUROLOGICAL", "meddra_pt": "10034620", "soc": "Nervous system disorders"},
    
    # Allergies
    {"term": "Seasonal Allergies", "category": "ALLERGY", "meddra_pt": "10039101", "soc": "Immune system disorders"},
    {"term": "Drug Allergy", "category": "ALLERGY", "meddra_pt": "10013700", "soc": "Immune system disorders"},
]


def get_meddra_for_ae(ae_term: str) -> dict[str, Any] | None:
    """Look up MedDRA coding for an adverse event term."""
    for ae in MEDDRA_ADVERSE_EVENTS:
        if ae["pt_name"].lower() == ae_term.lower():
            return ae
    return None


def get_lab_reference(test_code: str) -> dict[str, Any] | None:
    """Look up reference data for a lab test."""
    for lab in LAB_TESTS:
        if lab["test"] == test_code:
            return lab
    return None


def get_vital_reference(test_code: str) -> dict[str, Any] | None:
    """Look up reference data for a vital sign."""
    for vs in VITAL_SIGNS:
        if vs["test"] == test_code:
            return vs
    return None


__all__ = [
    "MEDDRA_ADVERSE_EVENTS",
    "LAB_TESTS",
    "VITAL_SIGNS",
    "THERAPEUTIC_AREAS",
    "CONCOMITANT_MEDICATIONS",
    "MEDICAL_HISTORY_ITEMS",
    "get_meddra_for_ae",
    "get_lab_reference",
    "get_vital_reference",
]

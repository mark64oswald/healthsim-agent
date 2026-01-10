"""Auto-naming service for HealthSim cohorts.

Generates descriptive cohort names from generation context,
following the pattern: {keywords}-{YYYYMMDD}
"""

import re
from datetime import datetime

# Common words to exclude from auto-generated names
STOP_WORDS: set[str] = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'some', 'any', 'no', 'not', 'all', 'each', 'every', 'both', 'few',
    'more', 'most', 'other', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'between', 'under', 'again', 'further',
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
    'our', 'ours', 'you', 'your', 'yours', 'he', 'him', 'his', 'she',
    'her', 'hers', 'it', 'its', 'they', 'them', 'their', 'what', 'which',
    'who', 'whom', 'generate', 'create', 'make', 'build', 'add', 'new',
    'please', 'want', 'like', 'need', 'help', 'show', 'give', 'get',
}

# Healthcare-relevant keywords to prioritize
HEALTHCARE_KEYWORDS: set[str] = {
    # Conditions
    'diabetes', 'diabetic', 'hypertension', 'cardiac', 'heart', 'cancer',
    'oncology', 'copd', 'asthma', 'respiratory', 'renal', 'kidney',
    'hepatic', 'liver', 'neurological', 'stroke', 'alzheimer', 'dementia',
    'arthritis', 'obesity', 'depression', 'anxiety', 'mental', 'psychiatric',
    # Demographics
    'medicare', 'medicaid', 'pediatric', 'geriatric', 'elderly', 'adult',
    'child', 'infant', 'neonatal', 'pregnant', 'maternal', 'veteran',
    # Care settings
    'emergency', 'inpatient', 'outpatient', 'ambulatory', 'primary',
    'specialty', 'urgent', 'icu', 'surgical', 'rehabilitation',
    # Entity types
    'patient', 'patients', 'member', 'members', 'claim', 'claims',
    'encounter', 'encounters', 'prescription', 'prescriptions',
    'subject', 'subjects', 'trial', 'study', 'cohort',
    # Products
    'pharmacy', 'rx', 'drug', 'medication', 'lab', 'diagnostic',
}


def extract_keywords(
    context: str | None = None,
    entity_type: str | None = None,
    max_keywords: int = 3,
) -> list[str]:
    """Extract meaningful keywords from generation context."""
    keywords: list[str] = []
    
    if context:
        words = re.findall(r'[a-zA-Z]+', context.lower())
        candidates = [w for w in words if w not in STOP_WORDS and len(w) >= 3]
        
        healthcare = [w for w in candidates if w in HEALTHCARE_KEYWORDS]
        other = [w for w in candidates if w not in HEALTHCARE_KEYWORDS]
        
        keywords = healthcare[:max_keywords]
        if len(keywords) < max_keywords:
            keywords.extend(other[:max_keywords - len(keywords)])
    
    if entity_type:
        entity_word = entity_type.lower().rstrip('s')
        plural = entity_word + 's'
        if plural not in keywords and entity_word not in keywords:
            keywords.append(plural)
    
    return keywords[:max_keywords]


def sanitize_name(name: str) -> str:
    """Sanitize a cohort name for safe storage."""
    name = name.lower()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^a-z0-9-]', '', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    if len(name) > 50:
        name = name[:50].rstrip('-')
    return name


def ensure_unique_name(base_name: str, existing_names: set[str] | None = None) -> str:
    """Ensure cohort name is unique by appending counter if needed."""
    if existing_names is None:
        return base_name
    
    if base_name not in existing_names:
        return base_name
    
    counter = 2
    while True:
        candidate = f"{base_name}-{counter}"
        if candidate not in existing_names:
            return candidate
        counter += 1
        if counter > 1000:
            timestamp = datetime.utcnow().strftime('%H%M%S')
            return f"{base_name}-{timestamp}"


def generate_cohort_name(
    keywords: list[str] | None = None,
    context: str | None = None,
    entity_type: str | None = None,
    prefix: str | None = None,
    include_date: bool = True,
    existing_names: set[str] | None = None,
) -> str:
    """Generate a unique, descriptive cohort name."""
    parts: list[str] = []
    
    if prefix:
        parts.append(sanitize_name(prefix))
    
    if keywords:
        parts.extend([sanitize_name(k) for k in keywords[:3]])
    elif context:
        extracted = extract_keywords(context, entity_type)
        parts.extend([sanitize_name(k) for k in extracted])
    elif entity_type:
        parts.append(sanitize_name(entity_type))
    
    if not parts:
        parts = ['cohort']
    
    base_name = '-'.join(parts)
    
    if include_date:
        date_suffix = datetime.utcnow().strftime('%Y%m%d')
        base_name = f"{base_name}-{date_suffix}"
    
    return ensure_unique_name(base_name, existing_names)


def parse_cohort_name(name: str) -> dict:
    """Parse a cohort name into its components."""
    result = {'keywords': [], 'date': None, 'counter': None}
    parts = name.split('-')
    
    if parts and parts[-1].isdigit() and len(parts[-1]) <= 3:
        result['counter'] = int(parts[-1])
        parts = parts[:-1]
    
    if parts and len(parts[-1]) == 8 and parts[-1].startswith('20'):
        try:
            datetime.strptime(parts[-1], '%Y%m%d')
            result['date'] = parts[-1]
            parts = parts[:-1]
        except ValueError:
            pass
    
    result['keywords'] = parts
    return result

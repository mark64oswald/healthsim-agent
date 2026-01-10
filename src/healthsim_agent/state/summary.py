"""
Cohort summary generation for context-efficient loading.

Generates statistical summaries that fit within token budget (~500 tokens)
while providing enough information for generation consistency.

This implements the "summary-in-context" part of the Structured RAG pattern:
- Full data stays in DuckDB
- Only summary + samples loaded to conversation
- Queries retrieve specific data on demand

Ported from: healthsim-workspace/packages/core/src/healthsim/state/summary.py
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any
import json


@dataclass
class CohortSummary:
    """
    Token-efficient cohort summary.
    
    Target budget:
    - Metadata: ~100 tokens
    - Entity counts: ~100 tokens
    - Statistics: ~300 tokens
    - Samples: ~3000 tokens (3 per major type)
    
    Total: ~3,500 tokens for full summary with samples
    """
    
    cohort_id: str
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    # Entity counts by type
    entity_counts: dict[str, int] = field(default_factory=dict)
    
    # Aggregate statistics
    statistics: dict[str, Any] = field(default_factory=dict)
    
    # Sample entities for pattern consistency
    samples: dict[str, list[dict]] = field(default_factory=dict)
    
    # Tags for organization
    tags: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'cohort_id': self.cohort_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'entity_counts': self.entity_counts,
            'statistics': self.statistics,
            'samples': self.samples,
            'tags': self.tags,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CohortSummary':
        """Create from dictionary."""
        return cls(
            cohort_id=data['cohort_id'],
            name=data['name'],
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            entity_counts=data.get('entity_counts', {}),
            statistics=data.get('statistics', {}),
            samples=data.get('samples', {}),
            tags=data.get('tags', []),
        )
    
    def total_entities(self) -> int:
        """Get total entity count across all types."""
        return sum(self.entity_counts.values())
    
    def token_estimate(self) -> int:
        """
        Estimate token count for this summary.
        
        Rough heuristic: ~4 characters per token for JSON.
        """
        json_str = self.to_json(indent=None)
        return len(json_str) // 4


# Entity type to table mapping for counts
ENTITY_COUNT_TABLES = {
    # PatientSim
    'patients': 'patients',
    'encounters': 'encounters',
    'diagnoses': 'diagnoses',
    'procedures': 'procedures',
    'lab_results': 'lab_results',
    'medications': 'medications',
    'allergies': 'allergies',
    'vitals': 'vital_signs',
    
    # MemberSim
    'members': 'members',
    'claims': 'claims',
    'claim_lines': 'claim_lines',
    'authorizations': 'authorizations',
    'accumulators': 'accumulators',
    
    # RxMemberSim
    'rx_members': 'rx_members',
    'prescriptions': 'prescriptions',
    'pharmacy_claims': 'pharmacy_claims',
    'dur_alerts': 'dur_alerts',
    
    # TrialSim
    'studies': 'studies',
    'sites': 'sites',
    'subjects': 'subjects',
    'adverse_events': 'adverse_events',
    'actual_visits': 'actual_visits',
    
    # PopulationSim
    'population_profiles': 'population_profiles',
    'cohort_specifications': 'cohort_specifications',
    
    # NetworkSim
    'networks': 'networks',
    'network_providers': 'network_providers',
    'network_facilities': 'network_facilities',
}


class SummaryGenerator:
    """
    Generates cohort summaries for context-efficient loading.
    
    This class provides methods to generate statistical summaries
    that fit within token budgets while maintaining pattern consistency.
    
    Usage:
        generator = SummaryGenerator(connection)
        summary = generator.generate(cohort_id)
    """
    
    def __init__(self, connection=None):
        """
        Initialize the summary generator.
        
        Args:
            connection: DuckDB connection (lazy loaded if not provided)
        """
        self._conn = connection
    
    @property
    def conn(self):
        """Get database connection."""
        if self._conn is None:
            from healthsim_agent.database import DatabaseConnection
            db_path = "data/healthsim-reference.duckdb"
            self._conn = DatabaseConnection(db_path)
        return self._conn
    
    def get_entity_counts(self, cohort_id: str) -> dict[str, int]:
        """Get entity counts for all tables in a cohort."""
        counts = {}
        
        for entity_type, table_name in ENTITY_COUNT_TABLES.items():
            try:
                result = self.conn.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE cohort_id = ?
                """, [cohort_id])
                
                if result.rows:
                    count = result.rows[0][0]
                    if count > 0:
                        counts[entity_type] = count
            except Exception:
                # Table may not exist or have cohort_id column
                pass
        
        return counts
    
    def calculate_patient_statistics(self, cohort_id: str) -> dict[str, Any]:
        """Calculate statistics for patient data."""
        stats = {}
        
        try:
            # Age statistics using DuckDB's date functions
            result = self.conn.execute("""
                SELECT 
                    MIN(EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INT) as min_age,
                    MAX(EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INT) as max_age,
                    AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::DOUBLE) as avg_age
                FROM patients
                WHERE cohort_id = ? AND birth_date IS NOT NULL
            """, [cohort_id])
            
            if result.rows and result.rows[0][0] is not None:
                row = result.rows[0]
                stats['age_range'] = {
                    'min': row[0],
                    'max': row[1],
                    'avg': round(row[2], 1) if row[2] else None
                }
            
            # Gender distribution
            result = self.conn.execute("""
                SELECT gender, COUNT(*) as count
                FROM patients
                WHERE cohort_id = ?
                GROUP BY gender
            """, [cohort_id])
            
            if result.rows:
                stats['gender_distribution'] = {
                    row[0]: row[1] for row in result.rows if row[0]
                }
            
        except Exception:
            pass
        
        return stats
    
    def calculate_encounter_statistics(self, cohort_id: str) -> dict[str, Any]:
        """Calculate statistics for encounter data."""
        stats = {}
        
        try:
            # Date range
            result = self.conn.execute("""
                SELECT 
                    MIN(CAST(admission_time AS DATE)) as min_date,
                    MAX(CAST(admission_time AS DATE)) as max_date
                FROM encounters
                WHERE cohort_id = ? AND admission_time IS NOT NULL
            """, [cohort_id])
            
            if result.rows and result.rows[0][0]:
                row = result.rows[0]
                stats['date_range'] = {
                    'min': str(row[0]),
                    'max': str(row[1])
                }
            
            # Encounter class distribution
            result = self.conn.execute("""
                SELECT class_code, COUNT(*) as count
                FROM encounters
                WHERE cohort_id = ?
                GROUP BY class_code
                ORDER BY count DESC
                LIMIT 5
            """, [cohort_id])
            
            if result.rows:
                stats['encounter_types'] = {
                    row[0]: row[1] for row in result.rows if row[0]
                }
            
        except Exception:
            pass
        
        return stats
    
    def calculate_claims_statistics(self, cohort_id: str) -> dict[str, Any]:
        """Calculate statistics for claims data."""
        stats = {}
        
        try:
            # Financial totals
            result = self.conn.execute("""
                SELECT 
                    SUM(total_charge) as total_billed,
                    SUM(total_paid) as total_paid,
                    SUM(patient_responsibility) as total_patient_resp,
                    AVG(total_charge) as avg_charge
                FROM claims
                WHERE cohort_id = ?
            """, [cohort_id])
            
            if result.rows and result.rows[0][0]:
                row = result.rows[0]
                stats['financials'] = {
                    'total_billed': round(row[0], 2),
                    'total_paid': round(row[1], 2) if row[1] else 0,
                    'total_patient_resp': round(row[2], 2) if row[2] else 0,
                    'avg_charge': round(row[3], 2) if row[3] else 0
                }
            
            # Claim type distribution
            result = self.conn.execute("""
                SELECT claim_type, COUNT(*) as count
                FROM claims
                WHERE cohort_id = ?
                GROUP BY claim_type
            """, [cohort_id])
            
            if result.rows:
                stats['claim_types'] = {
                    row[0]: row[1] for row in result.rows if row[0]
                }
            
        except Exception:
            pass
        
        return stats
    
    def calculate_diagnosis_statistics(self, cohort_id: str) -> dict[str, Any]:
        """Calculate statistics for diagnosis data."""
        stats = {}
        
        try:
            # Top diagnoses
            result = self.conn.execute("""
                SELECT code, description, COUNT(*) as count
                FROM diagnoses
                WHERE cohort_id = ?
                GROUP BY code, description
                ORDER BY count DESC
                LIMIT 5
            """, [cohort_id])
            
            if result.rows:
                stats['top_diagnoses'] = [
                    {'code': row[0], 'description': row[1], 'count': row[2]}
                    for row in result.rows if row[0]
                ]
            
        except Exception:
            pass
        
        return stats
    
    def get_diverse_samples(
        self,
        cohort_id: str,
        entity_type: str,
        table_name: str,
        count: int = 3,
    ) -> list[dict]:
        """
        Get diverse sample entities for pattern consistency.
        
        Tries to select samples that show variety (e.g., different genders,
        age ranges, conditions) rather than just random selection.
        """
        samples = []
        
        try:
            # Get all rows ordered by created_at
            result = self.conn.execute(f"""
                SELECT * FROM {table_name}
                WHERE cohort_id = ?
                ORDER BY created_at
            """, [cohort_id])
            
            if result.rows:
                columns = result.columns
                total = len(result.rows)
                
                if total <= count:
                    indices = list(range(total))
                else:
                    # Take evenly spaced samples
                    step = total / count
                    indices = [int(i * step) for i in range(count)]
                
                for idx in indices:
                    row = result.rows[idx]
                    sample = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert special types to strings
                        if isinstance(value, (datetime, date)):
                            value = str(value)
                        # Skip internal columns
                        if col not in ('cohort_id', 'created_at', 'generation_seed'):
                            sample[col] = value
                    samples.append(sample)
            
        except Exception:
            pass
        
        return samples
    
    def generate(
        self,
        cohort_id: str,
        include_samples: bool = True,
        samples_per_type: int = 3,
    ) -> CohortSummary:
        """
        Generate a token-efficient summary of a cohort.
        
        Args:
            cohort_id: UUID of the cohort
            include_samples: Whether to include sample entities
            samples_per_type: Number of samples per major entity type
            
        Returns:
            CohortSummary with counts, statistics, and optional samples
            
        Target token budget:
        - Without samples: ~500 tokens
        - With samples: ~3,500 tokens
        """
        # Get cohort metadata
        result = self.conn.execute("""
            SELECT id, name, description, created_at, updated_at
            FROM cohorts
            WHERE id = ?
        """, [cohort_id])
        
        if not result.rows:
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        row = result.rows[0]
        summary = CohortSummary(
            cohort_id=str(row[0]),
            name=row[1],
            description=row[2],
            created_at=row[3],
            updated_at=row[4],
        )
        
        # Get tags
        tags_result = self.conn.execute("""
            SELECT tag FROM cohort_tags
            WHERE cohort_id = ?
            ORDER BY tag
        """, [cohort_id])
        summary.tags = [row[0] for row in tags_result.rows] if tags_result.rows else []
        
        # Get entity counts
        summary.entity_counts = self.get_entity_counts(cohort_id)
        
        # Calculate statistics based on what entities exist
        statistics = {}
        
        if summary.entity_counts.get('patients', 0) > 0:
            statistics.update(self.calculate_patient_statistics(cohort_id))
        
        if summary.entity_counts.get('encounters', 0) > 0:
            statistics.update(self.calculate_encounter_statistics(cohort_id))
        
        if summary.entity_counts.get('claims', 0) > 0:
            statistics.update(self.calculate_claims_statistics(cohort_id))
        
        if summary.entity_counts.get('diagnoses', 0) > 0:
            statistics.update(self.calculate_diagnosis_statistics(cohort_id))
        
        summary.statistics = statistics
        
        # Get samples if requested
        if include_samples:
            samples = {}
            
            # Sample major entity types that have data
            sample_types = [
                ('patients', 'patients'),
                ('encounters', 'encounters'),
                ('members', 'members'),
                ('claims', 'claims'),
                ('subjects', 'subjects'),
                ('prescriptions', 'prescriptions'),
            ]
            
            for entity_type, table_name in sample_types:
                if summary.entity_counts.get(entity_type, 0) > 0:
                    entity_samples = self.get_diverse_samples(
                        cohort_id, entity_type, table_name,
                        count=samples_per_type
                    )
                    if entity_samples:
                        samples[entity_type] = entity_samples
            
            summary.samples = samples
        
        return summary


def get_cohort_by_name(name: str, connection=None) -> str | None:
    """
    Find cohort ID by name (fuzzy match).
    
    Args:
        name: Cohort name to search for
        connection: Optional database connection
        
    Returns:
        Cohort ID if found, None otherwise
    """
    if connection is None:
        from healthsim_agent.database import DatabaseConnection
        connection = DatabaseConnection("data/healthsim-reference.duckdb")
    
    # Try exact match first
    result = connection.execute("""
        SELECT id FROM cohorts
        WHERE name = ?
    """, [name])
    
    if result.rows:
        return str(result.rows[0][0])
    
    # Try case-insensitive match
    result = connection.execute("""
        SELECT id FROM cohorts
        WHERE LOWER(name) = LOWER(?)
    """, [name])
    
    if result.rows:
        return str(result.rows[0][0])
    
    # Try contains match
    result = connection.execute("""
        SELECT id FROM cohorts
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY updated_at DESC
        LIMIT 1
    """, [f"%{name}%"])
    
    if result.rows:
        return str(result.rows[0][0])
    
    return None


def generate_summary(
    cohort_id: str,
    include_samples: bool = True,
    samples_per_type: int = 3,
    connection=None,
) -> CohortSummary:
    """
    Generate a token-efficient summary of a cohort.
    
    Convenience function that wraps SummaryGenerator.
    
    Args:
        cohort_id: UUID of the cohort
        include_samples: Whether to include sample entities
        samples_per_type: Number of samples per major entity type
        connection: Optional database connection
        
    Returns:
        CohortSummary with counts, statistics, and optional samples
    """
    generator = SummaryGenerator(connection)
    return generator.generate(cohort_id, include_samples, samples_per_type)

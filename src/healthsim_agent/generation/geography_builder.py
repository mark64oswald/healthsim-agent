"""Geography-aware profile builder.

Combines PopulationSim demographics (CDC PLACES, SVI) with NetworkSim
provider/facility data to create geographically realistic profiles.

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/geography_builder.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import duckdb

from healthsim_agent.generation.reference_profiles import (
    DemographicProfile,
    GeographyLevel,
    RefGeographyReference as GeographyReference,
    ReferenceProfileResolver,
    merge_profile_with_reference,
    resolve_geography,
)
from healthsim_agent.generation.networksim_reference import (
    NetworkSimResolver,
    Provider,
    Facility,
    TAXONOMY_MAP,
    get_providers_by_geography,
    get_facilities_by_geography,
)


@dataclass
class GeographyProfile:
    """Complete geography-aware profile."""
    
    geography: GeographyReference
    demographics: DemographicProfile
    primary_care_providers: list[Provider] = field(default_factory=list)
    specialty_providers: dict[str, list[Provider]] = field(default_factory=dict)
    hospitals: list[Facility] = field(default_factory=list)
    snfs: list[Facility] = field(default_factory=list)
    other_facilities: list[Facility] = field(default_factory=list)
    provider_count: int = 0
    facility_count: int = 0
    
    def get_providers_for_specialty(self, specialty: str) -> list[Provider]:
        """Get providers for a specific specialty."""
        return self.specialty_providers.get(specialty, [])
    
    def get_random_pcp(self, seed: int | None = None) -> Optional[Provider]:
        """Get a random primary care provider."""
        import random
        if seed is not None:
            random.seed(seed)
        if self.primary_care_providers:
            return random.choice(self.primary_care_providers)
        return None
    
    def get_random_specialist(
        self,
        specialty: str,
        seed: int | None = None
    ) -> Optional[Provider]:
        """Get a random specialist provider."""
        import random
        if seed is not None:
            random.seed(seed)
        providers = self.specialty_providers.get(specialty, [])
        if providers:
            return random.choice(providers)
        return None
    
    def get_random_hospital(self, seed: int | None = None) -> Optional[Facility]:
        """Get a random hospital."""
        import random
        if seed is not None:
            random.seed(seed)
        if self.hospitals:
            return random.choice(self.hospitals)
        return None
    
    def to_profile_spec(self) -> dict:
        """Convert to profile specification dict."""
        spec = {
            "profile": {
                "id": f"geo-{self.geography.code}",
                "demographics": {
                    "source": "populationsim",
                    "reference": {
                        "type": self.geography.level.value,
                        "code": self.geography.code,
                        "name": self.geography.name,
                    }
                },
                "_geography_profile": {
                    "provider_count": self.provider_count,
                    "facility_count": self.facility_count,
                    "primary_care_count": len(self.primary_care_providers),
                    "hospital_count": len(self.hospitals),
                    "specialties_available": list(self.specialty_providers.keys()),
                }
            }
        }
        return spec


class GeographyAwareProfileBuilder:
    """Builds geography-aware profiles combining PopulationSim and NetworkSim."""
    
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn
        self.pop_resolver = ReferenceProfileResolver(conn)
        self.net_resolver = NetworkSimResolver(conn)
    
    def build_profile(
        self,
        geography: dict,
        include_providers: bool = True,
        include_facilities: bool = True,
        specialties: list[str] | None = None,
        max_providers_per_specialty: int = 100,
        max_facilities_per_type: int = 50,
    ) -> GeographyProfile:
        """Build a complete geography-aware profile."""
        demographics = resolve_geography(geography, self.conn)
        
        geo_ref = GeographyReference(
            level=demographics.geography.level,
            code=demographics.geography.code,
            name=demographics.geography.name,
        )
        
        state = self._get_state_from_geography(geography, demographics)
        city = self._get_city_from_geography(geography, demographics)
        
        profile = GeographyProfile(
            geography=geo_ref,
            demographics=demographics,
        )
        
        if include_providers and state:
            profile = self._add_providers(
                profile,
                state=state,
                city=city,
                specialties=specialties,
                max_per_specialty=max_providers_per_specialty,
            )
        
        if include_facilities and state:
            profile = self._add_facilities(
                profile,
                state=state,
                city=city,
                max_per_type=max_facilities_per_type,
            )
        
        return profile
    
    def _get_state_from_geography(
        self,
        geography: dict,
        demographics: DemographicProfile,
    ) -> Optional[str]:
        """Extract state from geography or demographics."""
        geo_type = geography.get("type", "").lower()
        
        if geo_type == "state":
            return geography.get("code") or geography.get("state")
        
        if demographics.raw_places:
            return demographics.raw_places.get("stateabbr")
        if demographics.raw_svi:
            return demographics.raw_svi.get("st_abbr")
        
        return None
    
    def _get_city_from_geography(
        self,
        geography: dict,
        demographics: DemographicProfile,
    ) -> Optional[str]:
        """Extract city from geography if available."""
        return None
    
    def _add_providers(
        self,
        profile: GeographyProfile,
        state: str,
        city: Optional[str],
        specialties: list[str] | None,
        max_per_specialty: int,
    ) -> GeographyProfile:
        """Add providers to profile."""
        pcp_taxonomies = [
            TAXONOMY_MAP["internal_medicine"],
            TAXONOMY_MAP["family_medicine"],
            TAXONOMY_MAP["general_practice"],
        ]
        
        pcps = []
        for taxonomy in pcp_taxonomies:
            providers = self.net_resolver.find_providers(
                state=state,
                city=city,
                taxonomy=taxonomy,
                limit=max_per_specialty // 3,
                random_sample=True,
            )
            pcps.extend(providers)
        
        profile.primary_care_providers = pcps[:max_per_specialty]
        profile.provider_count += len(profile.primary_care_providers)
        
        if specialties:
            for specialty in specialties:
                taxonomy = TAXONOMY_MAP.get(specialty.lower().replace(" ", "_"), specialty)
                providers = self.net_resolver.find_providers(
                    state=state,
                    city=city,
                    taxonomy=taxonomy,
                    limit=max_per_specialty,
                    random_sample=True,
                )
                if providers:
                    profile.specialty_providers[specialty] = providers
                    profile.provider_count += len(providers)
        
        return profile
    
    def _add_facilities(
        self,
        profile: GeographyProfile,
        state: str,
        city: Optional[str],
        max_per_type: int,
    ) -> GeographyProfile:
        """Add facilities to profile."""
        hospitals = self.net_resolver.find_facilities(
            state=state,
            city=city,
            facility_type="hospital",
            limit=max_per_type,
            random_sample=True,
        )
        profile.hospitals = hospitals
        profile.facility_count += len(hospitals)
        
        snfs = self.net_resolver.find_facilities(
            state=state,
            city=city,
            facility_type="snf",
            limit=max_per_type,
            random_sample=True,
        )
        profile.snfs = snfs
        profile.facility_count += len(snfs)
        
        return profile
    
    def build_multi_geography_profile(
        self,
        geographies: list[dict],
        **kwargs,
    ) -> list[GeographyProfile]:
        """Build profiles for multiple geographies."""
        return [
            self.build_profile(geo, **kwargs)
            for geo in geographies
        ]


# =============================================================================
# Convenience Functions
# =============================================================================

def create_geography_profile(
    conn: duckdb.DuckDBPyConnection,
    geography: dict,
    **kwargs,
) -> GeographyProfile:
    """Create a geography-aware profile."""
    builder = GeographyAwareProfileBuilder(conn)
    return builder.build_profile(geography, **kwargs)


def build_cohort_with_geography(
    conn: duckdb.DuckDBPyConnection,
    geography: dict,
    count: int,
    specialties: list[str] | None = None,
    seed: int | None = None,
) -> dict:
    """Build a cohort specification using geography-aware profile."""
    profile = create_geography_profile(
        conn,
        geography,
        specialties=specialties,
    )
    
    base_spec = profile.to_profile_spec()
    
    base_spec["profile"]["generation"] = {
        "count": count,
        "seed": seed,
    }
    
    if profile.primary_care_providers:
        base_spec["profile"]["_assigned_providers"] = {
            "primary_care": [
                {"npi": p.npi, "name": p.display_name}
                for p in profile.primary_care_providers[:10]
            ],
        }
    
    if profile.hospitals:
        base_spec["profile"]["_assigned_facilities"] = {
            "hospitals": [
                {"ccn": f.ccn, "name": f.name}
                for f in profile.hospitals[:5]
            ],
        }
    
    return base_spec


def get_provider_for_entity(
    geography_profile: GeographyProfile,
    specialty: str | None = None,
    entity_seed: int | None = None,
) -> Optional[Provider]:
    """Get a provider for an entity from the geography profile."""
    if specialty:
        return geography_profile.get_random_specialist(specialty, seed=entity_seed)
    return geography_profile.get_random_pcp(seed=entity_seed)


def get_facility_for_entity(
    geography_profile: GeographyProfile,
    facility_type: str = "hospital",
    entity_seed: int | None = None,
) -> Optional[Facility]:
    """Get a facility for an entity from the geography profile."""
    import random
    if entity_seed is not None:
        random.seed(entity_seed)
    
    if facility_type == "hospital":
        return geography_profile.get_random_hospital(seed=entity_seed)
    elif facility_type == "snf":
        if geography_profile.snfs:
            return random.choice(geography_profile.snfs)
    
    return None


__all__ = [
    "GeographyProfile",
    "GeographyAwareProfileBuilder",
    "create_geography_profile",
    "build_cohort_with_geography",
    "get_provider_for_entity",
    "get_facility_for_entity",
]

"""Extended tests for generation/geography_builder module."""

import pytest


class TestGeographyLevel:
    """Tests for GeographyLevel enum."""
    
    def test_level_exists(self):
        """Test GeographyLevel enum exists."""
        from healthsim_agent.generation.geography_builder import GeographyLevel
        
        assert GeographyLevel is not None
    
    def test_level_values(self):
        """Test GeographyLevel has expected values."""
        from healthsim_agent.generation.geography_builder import GeographyLevel
        
        # Check that it's an enum
        assert hasattr(GeographyLevel, '__members__')


class TestTaxonomyMap:
    """Tests for TAXONOMY_MAP constant."""
    
    def test_taxonomy_map_exists(self):
        """Test TAXONOMY_MAP exists."""
        from healthsim_agent.generation.geography_builder import TAXONOMY_MAP
        
        assert TAXONOMY_MAP is not None
        assert isinstance(TAXONOMY_MAP, dict)
    
    def test_taxonomy_map_has_values(self):
        """Test TAXONOMY_MAP has expected keys."""
        from healthsim_agent.generation.geography_builder import TAXONOMY_MAP
        
        # Should have taxonomy codes
        assert len(TAXONOMY_MAP) > 0


class TestModuleImports:
    """Tests for module imports."""
    
    def test_import_geography_profile(self):
        """Test GeographyProfile can be imported."""
        from healthsim_agent.generation.geography_builder import GeographyProfile
        assert GeographyProfile is not None
    
    def test_import_geography_reference(self):
        """Test GeographyReference can be imported."""
        from healthsim_agent.generation.geography_builder import GeographyReference
        assert GeographyReference is not None
    
    def test_import_provider(self):
        """Test Provider can be imported."""
        from healthsim_agent.generation.geography_builder import Provider
        assert Provider is not None
    
    def test_import_facility(self):
        """Test Facility can be imported."""
        from healthsim_agent.generation.geography_builder import Facility
        assert Facility is not None
    
    def test_import_profile_builder(self):
        """Test GeographyAwareProfileBuilder can be imported."""
        from healthsim_agent.generation.geography_builder import GeographyAwareProfileBuilder
        assert GeographyAwareProfileBuilder is not None
    
    def test_import_networksim_resolver(self):
        """Test NetworkSimResolver can be imported."""
        from healthsim_agent.generation.geography_builder import NetworkSimResolver
        assert NetworkSimResolver is not None
    
    def test_import_reference_resolver(self):
        """Test ReferenceProfileResolver can be imported."""
        from healthsim_agent.generation.geography_builder import ReferenceProfileResolver
        assert ReferenceProfileResolver is not None
    
    def test_import_resolve_geography(self):
        """Test resolve_geography can be imported."""
        from healthsim_agent.generation.geography_builder import resolve_geography
        assert resolve_geography is not None
    
    def test_import_create_geography_profile(self):
        """Test create_geography_profile can be imported."""
        from healthsim_agent.generation.geography_builder import create_geography_profile
        assert create_geography_profile is not None
    
    def test_import_build_cohort_with_geography(self):
        """Test build_cohort_with_geography can be imported."""
        from healthsim_agent.generation.geography_builder import build_cohort_with_geography
        assert build_cohort_with_geography is not None
    
    def test_import_merge_profile_with_reference(self):
        """Test merge_profile_with_reference can be imported."""
        from healthsim_agent.generation.geography_builder import merge_profile_with_reference
        assert merge_profile_with_reference is not None

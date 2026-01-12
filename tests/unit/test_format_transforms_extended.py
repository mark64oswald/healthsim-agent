"""Extended tests for format_tools transforms."""

import pytest


class TestTransformToFhir:
    """Tests for FHIR transformation."""
    
    def test_transform_patient(self):
        """Test transforming patient to FHIR."""
        from healthsim_agent.tools.format_tools import transform_to_fhir
        
        patient = {
            "id": "p1",
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1980-01-15",
            "gender": "M"
        }
        result = transform_to_fhir({"patients": [patient]})
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_fhir
        
        result = transform_to_fhir({})
        assert result is not None


class TestTransformToHl7v2:
    """Tests for HL7v2 transformation."""
    
    def test_transform_patient(self):
        """Test transforming patient to HL7v2."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        patient = {
            "id": "p1",
            "first_name": "Jane",
            "last_name": "Smith",
            "birth_date": "1990-05-20",
            "gender": "F"
        }
        result = transform_to_hl7v2({"patients": [patient]})
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        result = transform_to_hl7v2({})
        assert result is not None


class TestTransformToCcda:
    """Tests for C-CDA transformation."""
    
    def test_transform_patient(self):
        """Test transforming patient to C-CDA."""
        from healthsim_agent.tools.format_tools import transform_to_ccda
        
        patient = {"id": "p1", "first_name": "Test", "last_name": "Patient"}
        result = transform_to_ccda({"patients": [patient]})
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_ccda
        
        result = transform_to_ccda({})
        assert result is not None


class TestTransformToX12:
    """Tests for X12 transformation."""
    
    def test_transform_claim(self):
        """Test transforming claim to X12."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        data = {"claims": [{"id": "c1", "type": "PROFESSIONAL"}]}
        result = transform_to_x12(data)
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        result = transform_to_x12({})
        assert result is not None


class TestTransformToNcpdp:
    """Tests for NCPDP transformation."""
    
    def test_transform_rx_claim(self):
        """Test transforming Rx claim to NCPDP."""
        from healthsim_agent.tools.format_tools import transform_to_ncpdp
        
        data = {"rx_claims": [{"id": "rx1", "ndc": "12345678901"}]}
        result = transform_to_ncpdp(data)
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_ncpdp
        
        result = transform_to_ncpdp({})
        assert result is not None


class TestTransformToMimic:
    """Tests for MIMIC transformation."""
    
    def test_transform_patient(self):
        """Test transforming patient to MIMIC."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {"patients": [{"id": "p1"}]}
        result = transform_to_mimic(data)
        assert result is not None
    
    def test_transform_empty(self):
        """Test transforming empty data."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        result = transform_to_mimic({})
        assert result is not None


class TestListOutputFormats:
    """Tests for list_output_formats function."""
    
    def test_list_formats(self):
        """Test listing output formats."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        assert result is not None
        assert result.success is True
    
    def test_formats_include_fhir(self):
        """Test formats data is returned."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        # Check data is present
        assert result.data is not None

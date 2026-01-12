"""
Tests for person/identifiers module.

Covers:
- IdentifierType enum
- Identifier model properties (is_expired, is_valid)
- IdentifierSet collection operations
"""

import pytest
from datetime import date, timedelta


class TestIdentifierType:
    """Tests for IdentifierType enum."""
    
    def test_ssn_type(self):
        """Test SSN identifier type."""
        from healthsim_agent.person.identifiers import IdentifierType
        
        assert IdentifierType.SSN == "SSN"
        assert IdentifierType.SSN.value == "SSN"
    
    def test_drivers_license_type(self):
        """Test drivers license type."""
        from healthsim_agent.person.identifiers import IdentifierType
        
        assert IdentifierType.DRIVERS_LICENSE == "DL"
    
    def test_all_types_exist(self):
        """Test all expected identifier types exist."""
        from healthsim_agent.person.identifiers import IdentifierType
        
        expected = ["SSN", "DRIVERS_LICENSE", "PASSPORT", "NATIONAL_ID", "TAX_ID", "CUSTOM"]
        for name in expected:
            assert hasattr(IdentifierType, name)


class TestIdentifier:
    """Tests for Identifier model."""
    
    def test_create_basic_identifier(self):
        """Test creating a basic identifier."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        identifier = Identifier(
            type=IdentifierType.SSN,
            value="123-45-6789"
        )
        
        assert identifier.type == IdentifierType.SSN
        assert identifier.value == "123-45-6789"
        assert identifier.is_primary is True  # default
        assert identifier.system is None
        assert identifier.issuer is None
    
    def test_create_identifier_with_dates(self):
        """Test creating identifier with issue/expiry dates."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        issue = date(2020, 1, 1)
        expiry = date(2030, 1, 1)
        
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            issuer="US State Dept",
            issue_date=issue,
            expiry_date=expiry
        )
        
        assert identifier.issue_date == issue
        assert identifier.expiry_date == expiry
        assert identifier.issuer == "US State Dept"
    
    def test_is_expired_no_expiry_date(self):
        """Test is_expired returns False when no expiry date."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        identifier = Identifier(
            type=IdentifierType.SSN,
            value="123-45-6789"
        )
        
        assert identifier.is_expired is False
    
    def test_is_expired_future_date(self):
        """Test is_expired returns False for future expiry."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        future = date.today() + timedelta(days=365)
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            expiry_date=future
        )
        
        assert identifier.is_expired is False
    
    def test_is_expired_past_date(self):
        """Test is_expired returns True for past expiry."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        past = date.today() - timedelta(days=1)
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            expiry_date=past
        )
        
        assert identifier.is_expired is True
    
    def test_is_valid_no_dates(self):
        """Test is_valid returns True when no dates set."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        identifier = Identifier(
            type=IdentifierType.SSN,
            value="123-45-6789"
        )
        
        assert identifier.is_valid is True
    
    def test_is_valid_within_date_range(self):
        """Test is_valid returns True when within date range."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        past = date.today() - timedelta(days=365)
        future = date.today() + timedelta(days=365)
        
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            issue_date=past,
            expiry_date=future
        )
        
        assert identifier.is_valid is True
    
    def test_is_valid_false_when_not_yet_issued(self):
        """Test is_valid returns False when issue date is in future."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        future = date.today() + timedelta(days=30)
        
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            issue_date=future
        )
        
        assert identifier.is_valid is False
    
    def test_is_valid_false_when_expired(self):
        """Test is_valid returns False when expired."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        past_issue = date.today() - timedelta(days=365)
        past_expiry = date.today() - timedelta(days=1)
        
        identifier = Identifier(
            type=IdentifierType.PASSPORT,
            value="AB123456",
            issue_date=past_issue,
            expiry_date=past_expiry
        )
        
        assert identifier.is_valid is False
    
    def test_identifier_with_system(self):
        """Test identifier with system/namespace."""
        from healthsim_agent.person.identifiers import Identifier, IdentifierType
        
        identifier = Identifier(
            type=IdentifierType.CUSTOM,
            value="EMP123",
            system="urn:company:employee-id"
        )
        
        assert identifier.system == "urn:company:employee-id"


class TestIdentifierSet:
    """Tests for IdentifierSet collection."""
    
    def test_create_empty_set(self):
        """Test creating an empty identifier set."""
        from healthsim_agent.person.identifiers import IdentifierSet
        
        id_set = IdentifierSet()
        
        assert len(id_set) == 0
        assert id_set.identifiers == []
    
    def test_add_identifier(self):
        """Test adding an identifier to the set."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        identifier = Identifier(type=IdentifierType.SSN, value="123-45-6789")
        
        id_set.add(identifier)
        
        assert len(id_set) == 1
        assert id_set.identifiers[0].value == "123-45-6789"
    
    def test_get_by_type_found_primary(self):
        """Test get_by_type returns primary identifier first."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.SSN, value="111-11-1111", is_primary=False))
        id_set.add(Identifier(type=IdentifierType.SSN, value="222-22-2222", is_primary=True))
        
        result = id_set.get_by_type(IdentifierType.SSN)
        
        assert result is not None
        assert result.value == "222-22-2222"
    
    def test_get_by_type_falls_back_to_non_primary(self):
        """Test get_by_type returns non-primary if no primary exists."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.SSN, value="111-11-1111", is_primary=False))
        
        result = id_set.get_by_type(IdentifierType.SSN)
        
        assert result is not None
        assert result.value == "111-11-1111"
    
    def test_get_by_type_not_found(self):
        """Test get_by_type returns None when not found."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.SSN, value="123-45-6789"))
        
        result = id_set.get_by_type(IdentifierType.PASSPORT)
        
        assert result is None
    
    def test_get_all_by_type(self):
        """Test get_all_by_type returns all matching."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.PASSPORT, value="AB111"))
        id_set.add(Identifier(type=IdentifierType.SSN, value="123-45-6789"))
        id_set.add(Identifier(type=IdentifierType.PASSPORT, value="AB222"))
        
        results = id_set.get_all_by_type(IdentifierType.PASSPORT)
        
        assert len(results) == 2
        assert results[0].value == "AB111"
        assert results[1].value == "AB222"
    
    def test_get_all_by_type_empty(self):
        """Test get_all_by_type returns empty list when none found."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.SSN, value="123-45-6789"))
        
        results = id_set.get_all_by_type(IdentifierType.PASSPORT)
        
        assert results == []
    
    def test_get_by_system_found(self):
        """Test get_by_system returns matching identifier."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(
            type=IdentifierType.CUSTOM,
            value="EMP123",
            system="urn:company:employee-id"
        ))
        
        result = id_set.get_by_system("urn:company:employee-id")
        
        assert result is not None
        assert result.value == "EMP123"
    
    def test_get_by_system_not_found(self):
        """Test get_by_system returns None when not found."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(
            type=IdentifierType.SSN,
            value="123-45-6789"
        ))
        
        result = id_set.get_by_system("urn:company:employee-id")
        
        assert result is None
    
    def test_len(self):
        """Test __len__ returns correct count."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        assert len(id_set) == 0
        
        id_set.add(Identifier(type=IdentifierType.SSN, value="111"))
        assert len(id_set) == 1
        
        id_set.add(Identifier(type=IdentifierType.SSN, value="222"))
        assert len(id_set) == 2
    
    def test_iter(self):
        """Test __iter__ allows iteration."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        id_set = IdentifierSet()
        id_set.add(Identifier(type=IdentifierType.SSN, value="111"))
        id_set.add(Identifier(type=IdentifierType.PASSPORT, value="AB123"))
        
        values = [i.value for i in id_set]
        
        assert values == ["111", "AB123"]
    
    def test_create_with_initial_identifiers(self):
        """Test creating IdentifierSet with initial identifiers."""
        from healthsim_agent.person.identifiers import IdentifierSet, Identifier, IdentifierType
        
        identifiers = [
            Identifier(type=IdentifierType.SSN, value="111"),
            Identifier(type=IdentifierType.PASSPORT, value="AB123"),
        ]
        
        id_set = IdentifierSet(identifiers=identifiers)
        
        assert len(id_set) == 2

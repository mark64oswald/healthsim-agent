"""
Tests for BaseGenerator and PersonGenerator.

Covers:
- BaseGenerator initialization and seed management
- Random value generation methods
- PersonGenerator person creation
- Name, birth date, address, contact generation
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from healthsim_agent.generation.base import BaseGenerator, PersonGenerator
from healthsim_agent.person.demographics import Gender


class TestBaseGeneratorInit:
    """Tests for BaseGenerator initialization."""
    
    def test_init_without_seed(self):
        """Test initialization without seed."""
        gen = BaseGenerator()
        
        assert gen.seed_manager is not None
        assert gen.faker is not None
    
    def test_init_with_seed(self):
        """Test initialization with specific seed."""
        gen = BaseGenerator(seed=42)
        
        assert gen.seed_manager is not None
        assert gen.faker is not None
    
    def test_init_with_locale(self):
        """Test initialization with locale."""
        gen = BaseGenerator(locale="de_DE")
        
        assert gen.faker is not None
    
    def test_rng_property(self):
        """Test rng property returns random generator."""
        gen = BaseGenerator(seed=42)
        
        rng = gen.rng
        assert rng is not None
        # Should be able to generate random values
        val = rng.random()
        assert 0 <= val <= 1


class TestBaseGeneratorReset:
    """Tests for BaseGenerator reset functionality."""
    
    def test_reset_produces_same_sequence(self):
        """Test reset produces same random sequence."""
        gen = BaseGenerator(seed=42)
        
        # Generate some values
        val1 = gen.random_int(1, 100)
        val2 = gen.random_int(1, 100)
        
        # Reset
        gen.reset()
        
        # Should get same values again
        val1_again = gen.random_int(1, 100)
        val2_again = gen.random_int(1, 100)
        
        assert val1 == val1_again
        assert val2 == val2_again


class TestGenerateId:
    """Tests for generate_id method."""
    
    def test_generate_id_no_prefix(self):
        """Test generate_id without prefix."""
        gen = BaseGenerator(seed=42)
        
        id1 = gen.generate_id()
        
        assert len(id1) == 8
        assert id1.isupper()
    
    def test_generate_id_with_prefix(self):
        """Test generate_id with prefix."""
        gen = BaseGenerator(seed=42)
        
        id1 = gen.generate_id("PATIENT")
        
        assert id1.startswith("PATIENT-")
        assert len(id1) == 16  # "PATIENT-" (8) + 8 char hex
    
    def test_generate_id_unique(self):
        """Test generate_id produces unique IDs."""
        gen = BaseGenerator(seed=42)
        
        ids = [gen.generate_id() for _ in range(100)]
        
        assert len(ids) == len(set(ids))


class TestRandomChoice:
    """Tests for random_choice method."""
    
    def test_random_choice_returns_from_list(self):
        """Test random_choice returns item from list."""
        gen = BaseGenerator(seed=42)
        
        options = ["A", "B", "C", "D"]
        choice = gen.random_choice(options)
        
        assert choice in options
    
    def test_random_choice_reproducible(self):
        """Test random_choice is reproducible with seed."""
        gen1 = BaseGenerator(seed=42)
        gen2 = BaseGenerator(seed=42)
        
        options = ["A", "B", "C", "D", "E"]
        
        choices1 = [gen1.random_choice(options) for _ in range(10)]
        choices2 = [gen2.random_choice(options) for _ in range(10)]
        
        assert choices1 == choices2


class TestRandomInt:
    """Tests for random_int method."""
    
    def test_random_int_in_range(self):
        """Test random_int returns value in range."""
        gen = BaseGenerator(seed=42)
        
        for _ in range(100):
            val = gen.random_int(10, 50)
            assert 10 <= val <= 50
    
    def test_random_int_boundary(self):
        """Test random_int handles boundary values."""
        gen = BaseGenerator(seed=42)
        
        # Same min and max
        val = gen.random_int(5, 5)
        assert val == 5


class TestRandomFloat:
    """Tests for random_float method."""
    
    def test_random_float_default_range(self):
        """Test random_float default range is 0-1."""
        gen = BaseGenerator(seed=42)
        
        for _ in range(100):
            val = gen.random_float()
            assert 0.0 <= val <= 1.0
    
    def test_random_float_custom_range(self):
        """Test random_float with custom range."""
        gen = BaseGenerator(seed=42)
        
        for _ in range(100):
            val = gen.random_float(10.0, 20.0)
            assert 10.0 <= val <= 20.0


class TestRandomBool:
    """Tests for random_bool method."""
    
    def test_random_bool_default_probability(self):
        """Test random_bool with default 50% probability."""
        gen = BaseGenerator(seed=42)
        
        results = [gen.random_bool() for _ in range(1000)]
        
        # Should have both True and False
        assert True in results
        assert False in results
        
        # Roughly 50/50 (within margin)
        true_count = sum(results)
        assert 400 <= true_count <= 600
    
    def test_random_bool_high_probability(self):
        """Test random_bool with high probability."""
        gen = BaseGenerator(seed=42)
        
        results = [gen.random_bool(0.9) for _ in range(100)]
        
        # Most should be True
        true_count = sum(results)
        assert true_count >= 80
    
    def test_random_bool_low_probability(self):
        """Test random_bool with low probability."""
        gen = BaseGenerator(seed=42)
        
        results = [gen.random_bool(0.1) for _ in range(100)]
        
        # Most should be False
        true_count = sum(results)
        assert true_count <= 20


class TestWeightedChoice:
    """Tests for weighted_choice method."""
    
    def test_weighted_choice_returns_option(self):
        """Test weighted_choice returns one of the options."""
        gen = BaseGenerator(seed=42)
        
        options = [("A", 0.5), ("B", 0.3), ("C", 0.2)]
        choice = gen.weighted_choice(options)
        
        assert choice in ["A", "B", "C"]
    
    def test_weighted_choice_respects_weights(self):
        """Test weighted_choice respects probability weights."""
        gen = BaseGenerator(seed=42)
        
        # Heavily weighted toward "A"
        options = [("A", 0.95), ("B", 0.05)]
        
        choices = [gen.weighted_choice(options) for _ in range(100)]
        a_count = sum(1 for c in choices if c == "A")
        
        # Should be mostly "A"
        assert a_count >= 85


class TestRandomDateBetween:
    """Tests for random_date_between method."""
    
    def test_random_date_in_range(self):
        """Test random_date_between returns date in range."""
        gen = BaseGenerator(seed=42)
        
        start = date(2020, 1, 1)
        end = date(2020, 12, 31)
        
        for _ in range(100):
            d = gen.random_date_between(start, end)
            assert start <= d <= end
    
    def test_random_date_same_day(self):
        """Test random_date_between with same start/end."""
        gen = BaseGenerator(seed=42)
        
        d = date(2020, 6, 15)
        result = gen.random_date_between(d, d)
        
        assert result == d


class TestRandomDatetimeBetween:
    """Tests for random_datetime_between method."""
    
    def test_random_datetime_in_range(self):
        """Test random_datetime_between returns datetime in range."""
        gen = BaseGenerator(seed=42)
        
        start = datetime(2020, 1, 1, 0, 0, 0)
        end = datetime(2020, 12, 31, 23, 59, 59)
        
        for _ in range(100):
            dt = gen.random_datetime_between(start, end)
            assert start <= dt <= end
    
    def test_random_datetime_same_moment(self):
        """Test random_datetime_between with same start/end."""
        gen = BaseGenerator(seed=42)
        
        dt = datetime(2020, 6, 15, 12, 30, 0)
        result = gen.random_datetime_between(dt, dt)
        
        assert result == dt


class TestPersonGeneratorInit:
    """Tests for PersonGenerator initialization."""
    
    def test_inherits_base_generator(self):
        """Test PersonGenerator inherits from BaseGenerator."""
        gen = PersonGenerator(seed=42)
        
        # Should have all BaseGenerator methods
        assert hasattr(gen, 'random_choice')
        assert hasattr(gen, 'random_int')
        assert hasattr(gen, 'faker')


class TestGeneratePerson:
    """Tests for generate_person method."""
    
    def test_generate_basic_person(self):
        """Test generating a basic person."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person()
        
        assert person.id.startswith("PERSON-")
        assert person.name is not None
        assert person.birth_date is not None
        assert person.gender in [Gender.MALE, Gender.FEMALE]
        assert person.address is not None
        assert person.contact is not None
    
    def test_generate_person_male(self):
        """Test generating a male person."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person(gender=Gender.MALE)
        
        assert person.gender == Gender.MALE
    
    def test_generate_person_female(self):
        """Test generating a female person."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person(gender=Gender.FEMALE)
        
        assert person.gender == Gender.FEMALE
    
    def test_generate_person_without_address(self):
        """Test generating person without address."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person(include_address=False)
        
        assert person.address is None
    
    def test_generate_person_without_contact(self):
        """Test generating person without contact."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person(include_contact=False)
        
        assert person.contact is None
    
    def test_generate_person_age_range(self):
        """Test generating person with specific age range."""
        gen = PersonGenerator(seed=42)
        
        person = gen.generate_person(age_range=(65, 75))
        
        today = date.today()
        age = (today - person.birth_date).days // 365
        
        assert 65 <= age <= 75


class TestGenerateName:
    """Tests for generate_name method."""
    
    def test_generate_name_male(self):
        """Test generating male name."""
        gen = PersonGenerator(seed=42)
        
        name = gen.generate_name(Gender.MALE)
        
        assert name.given_name is not None
        assert name.family_name is not None
    
    def test_generate_name_female(self):
        """Test generating female name."""
        gen = PersonGenerator(seed=42)
        
        name = gen.generate_name(Gender.FEMALE)
        
        assert name.given_name is not None
        assert name.family_name is not None
    
    def test_generate_name_no_gender(self):
        """Test generating name without gender."""
        gen = PersonGenerator(seed=42)
        
        name = gen.generate_name(None)
        
        assert name.given_name is not None
        assert name.family_name is not None
    
    def test_generate_name_may_have_middle(self):
        """Test generate_name may include middle name."""
        gen = PersonGenerator(seed=42)
        
        # Generate many names - some should have middle names
        names = [gen.generate_name(Gender.MALE) for _ in range(100)]
        
        has_middle = any(n.middle_name is not None for n in names)
        no_middle = any(n.middle_name is None for n in names)
        
        assert has_middle  # Some should have middle names
        assert no_middle   # Some should not


class TestGenerateBirthDate:
    """Tests for generate_birth_date method."""
    
    def test_generate_birth_date_in_range(self):
        """Test birth date produces correct age range."""
        gen = PersonGenerator(seed=42)
        
        birth_date = gen.generate_birth_date((30, 40))
        today = date.today()
        age = (today - birth_date).days // 365
        
        assert 30 <= age <= 40
    
    def test_generate_birth_date_elderly(self):
        """Test birth date for elderly age range."""
        gen = PersonGenerator(seed=42)
        
        birth_date = gen.generate_birth_date((80, 90))
        today = date.today()
        age = (today - birth_date).days // 365
        
        assert 80 <= age <= 90


class TestGenerateAddress:
    """Tests for generate_address method."""
    
    def test_generate_address_complete(self):
        """Test generate_address returns complete address."""
        gen = PersonGenerator(seed=42)
        
        address = gen.generate_address()
        
        assert address.street_address is not None
        assert address.city is not None
        assert address.state is not None
        assert address.postal_code is not None
        assert address.country == "US"


class TestGenerateContact:
    """Tests for generate_contact method."""
    
    def test_generate_contact_has_phone(self):
        """Test generate_contact has phone."""
        gen = PersonGenerator(seed=42)
        
        contact = gen.generate_contact()
        
        assert contact.phone is not None
        assert contact.email is not None
    
    def test_generate_contact_may_have_mobile(self):
        """Test generate_contact may have mobile phone."""
        gen = PersonGenerator(seed=42)
        
        # Generate many contacts - most should have mobile
        contacts = [gen.generate_contact() for _ in range(100)]
        
        has_mobile = sum(1 for c in contacts if c.phone_mobile is not None)
        
        # About 70% should have mobile
        assert has_mobile >= 50


class TestGenerateSSN:
    """Tests for generate_ssn method."""
    
    def test_generate_ssn_format(self):
        """Test generate_ssn returns SSN format."""
        gen = PersonGenerator(seed=42)
        
        ssn = gen.generate_ssn()
        
        # SSN format: XXX-XX-XXXX
        assert len(ssn) == 11
        assert ssn[3] == "-"
        assert ssn[6] == "-"
    
    def test_generate_ssn_unique(self):
        """Test generate_ssn produces unique values."""
        gen = PersonGenerator(seed=42)
        
        ssns = [gen.generate_ssn() for _ in range(100)]
        
        # All should be unique
        assert len(ssns) == len(set(ssns))


class TestReproducibility:
    """Tests for reproducibility with seeds."""
    
    def test_same_seed_same_person(self):
        """Test same seed produces identical person."""
        gen1 = PersonGenerator(seed=42)
        gen2 = PersonGenerator(seed=42)
        
        person1 = gen1.generate_person()
        person2 = gen2.generate_person()
        
        assert person1.name.given_name == person2.name.given_name
        assert person1.name.family_name == person2.name.family_name
        assert person1.birth_date == person2.birth_date
        assert person1.gender == person2.gender
    
    def test_different_seed_different_person(self):
        """Test different seeds produce different people."""
        gen1 = PersonGenerator(seed=42)
        gen2 = PersonGenerator(seed=999)
        
        person1 = gen1.generate_person()
        person2 = gen2.generate_person()
        
        # Very unlikely to match with different seeds
        assert (person1.name.given_name != person2.name.given_name or
                person1.name.family_name != person2.name.family_name or
                person1.birth_date != person2.birth_date)

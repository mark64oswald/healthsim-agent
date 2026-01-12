"""Extended tests for formats/transformer module."""

import pytest


class TestJsonTransformer:
    """Tests for JsonTransformer class."""
    
    def test_is_abstract(self):
        """Test that JsonTransformer is abstract."""
        from healthsim_agent.formats.transformer import JsonTransformer
        import inspect
        
        assert inspect.isabstract(JsonTransformer)
    
    def test_has_transform_method(self):
        """Test that JsonTransformer declares transform method."""
        from healthsim_agent.formats.transformer import JsonTransformer
        
        assert hasattr(JsonTransformer, 'transform')
    
    def test_cannot_instantiate(self):
        """Test that JsonTransformer cannot be instantiated directly."""
        from healthsim_agent.formats.transformer import JsonTransformer
        
        with pytest.raises(TypeError):
            JsonTransformer()


class TestCsvTransformer:
    """Tests for CsvTransformer class."""
    
    def test_is_abstract(self):
        """Test that CsvTransformer is abstract."""
        from healthsim_agent.formats.transformer import CsvTransformer
        import inspect
        
        assert inspect.isabstract(CsvTransformer)
    
    def test_has_transform_method(self):
        """Test that CsvTransformer declares transform method."""
        from healthsim_agent.formats.transformer import CsvTransformer
        
        assert hasattr(CsvTransformer, 'transform')
    
    def test_has_columns_method(self):
        """Test that CsvTransformer declares columns method."""
        from healthsim_agent.formats.transformer import CsvTransformer
        
        assert hasattr(CsvTransformer, 'columns')
    
    def test_cannot_instantiate(self):
        """Test that CsvTransformer cannot be instantiated directly."""
        from healthsim_agent.formats.transformer import CsvTransformer
        
        with pytest.raises(TypeError):
            CsvTransformer()


class TestTransformerBase:
    """Tests for Transformer base class."""
    
    def test_transformer_abstract(self):
        """Test that Transformer is abstract."""
        from healthsim_agent.formats.transformer import Transformer
        import inspect
        
        assert inspect.isabstract(Transformer)
    
    def test_transformer_has_transform(self):
        """Test that Transformer has transform method."""
        from healthsim_agent.formats.transformer import Transformer
        
        assert hasattr(Transformer, 'transform')

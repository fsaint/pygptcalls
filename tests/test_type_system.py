"""
Tests for type system functionality in pygptcalls.
"""
import unittest
from typing import List, Dict, Optional, Union
from datetime import datetime
import uuid

from pygptcalls.pygptcalls import (
    is_optional_type, 
    map_python_type_to_json_type,
    custom_serializer
)


class TestTypeSystem(unittest.TestCase):
    """Test type system functions."""
    
    def test_is_optional_type_basic(self):
        """Test basic optional type detection."""
        # Test Optional[str] which is Union[str, None]
        self.assertTrue(is_optional_type(Optional[str]))
        self.assertTrue(is_optional_type(Optional[int]))
        self.assertTrue(is_optional_type(Union[str, None]))
        self.assertTrue(is_optional_type(Union[int, None]))
        
    def test_is_optional_type_non_optional(self):
        """Test non-optional types."""
        self.assertFalse(is_optional_type(str))
        self.assertFalse(is_optional_type(int))
        self.assertFalse(is_optional_type(List[str]))
        self.assertFalse(is_optional_type(Dict[str, int]))
        
    def test_is_optional_type_complex_unions(self):
        """Test complex union types."""
        # Union with more than just None
        self.assertFalse(is_optional_type(Union[str, int]))
        # Union with None but also other types
        self.assertTrue(is_optional_type(Union[str, int, None]))
        
    def test_map_python_type_to_json_basic_types(self):
        """Test basic Python to JSON type mapping."""
        self.assertEqual(map_python_type_to_json_type(str), 'string')
        self.assertEqual(map_python_type_to_json_type(int), 'integer')
        self.assertEqual(map_python_type_to_json_type(float), 'number')
        self.assertEqual(map_python_type_to_json_type(bool), 'boolean')
        self.assertEqual(map_python_type_to_json_type(dict), 'object')
        self.assertEqual(map_python_type_to_json_type(list), 'array')
        self.assertEqual(map_python_type_to_json_type(type(None)), 'null')
        
    def test_map_python_type_to_json_optional_types(self):
        """Test optional type mapping."""
        # Optional types should map to their inner type
        self.assertEqual(map_python_type_to_json_type(Optional[str]), 'string')
        self.assertEqual(map_python_type_to_json_type(Optional[int]), 'integer')
        self.assertEqual(map_python_type_to_json_type(Optional[bool]), 'boolean')
        
    def test_map_python_type_to_json_complex_types(self):
        """Test complex type mapping."""
        # Complex types should map to their origin type
        self.assertEqual(map_python_type_to_json_type(List[str]), 'array')
        self.assertEqual(map_python_type_to_json_type(Dict[str, int]), 'object')
        self.assertEqual(map_python_type_to_json_type(List[Dict[str, int]]), 'array')
        
    def test_map_python_type_to_json_unknown_types(self):
        """Test unknown type mapping."""
        # Unknown types should default to 'string'
        class CustomType:
            pass
        
        self.assertEqual(map_python_type_to_json_type(CustomType), 'string')
        
    def test_custom_serializer_datetime(self):
        """Test datetime serialization."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = custom_serializer(dt)
        self.assertEqual(result, '2023-01-01T12:00:00')
        
    def test_custom_serializer_uuid(self):
        """Test UUID serialization."""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        result = custom_serializer(test_uuid)
        self.assertEqual(result, '12345678-1234-5678-1234-567812345678')
        
    def test_custom_serializer_unsupported_type(self):
        """Test unsupported type serialization raises error."""
        class UnsupportedType:
            pass
        
        obj = UnsupportedType()
        with self.assertRaises(TypeError) as context:
            custom_serializer(obj)
        
        self.assertIn("not serializable", str(context.exception))


if __name__ == '__main__':
    unittest.main()

"""
Tests for JSON schema generation in pygptcalls.
"""
import unittest
from typing import List, Dict, Optional
import json

from pygptcalls.pygptcalls import (
    generate_function_json,
    generate_function_json_from_list
)
from tests.test_utils import (
    create_test_function_simple,
    create_test_function_optional,
    create_test_function_complex_types,
    create_test_function_no_args,
    SAMPLE_FUNCTIONS
)


class TestJSONGeneration(unittest.TestCase):
    """Test JSON schema generation for OpenAI function calling."""
    
    def test_generate_function_json_from_list_basic(self):
        """Test basic JSON generation from function list."""
        functions = [create_test_function_simple]
        result = generate_function_json_from_list(functions)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        func_schema = result[0]
        self.assertEqual(func_schema['type'], 'function')
        self.assertIn('function', func_schema)
        
        function_def = func_schema['function']
        self.assertEqual(function_def['name'], 'create_test_function_simple')
        self.assertTrue(function_def['strict'])
        self.assertFalse(function_def['parameters']['additionalProperties'])
        
    def test_generate_function_json_from_list_parameters(self):
        """Test parameter handling in JSON generation."""
        functions = [create_test_function_simple]
        result = generate_function_json_from_list(functions)
        
        params = result[0]['function']['parameters']
        self.assertEqual(params['type'], 'object')
        
        # Check properties
        properties = params['properties']
        self.assertIn('name', properties)
        self.assertIn('age', properties)
        
        # Check name parameter
        name_param = properties['name']
        self.assertEqual(name_param['name'], 'name')
        self.assertEqual(name_param['type'], 'string')
        self.assertEqual(name_param['description'], "The person's name")
        
        # Check age parameter
        age_param = properties['age']
        self.assertEqual(age_param['name'], 'age')
        self.assertEqual(age_param['type'], 'integer')
        self.assertEqual(age_param['description'], "The person's age")
        
        # Check required parameters
        required = params['required']
        self.assertIn('name', required)
        self.assertIn('age', required)
        self.assertEqual(len(required), 2)
        
    def test_generate_function_json_from_list_optional_params(self):
        """Test handling of optional parameters."""
        functions = [create_test_function_optional]
        result = generate_function_json_from_list(functions)
        
        params = result[0]['function']['parameters']
        required = params['required']
        
        # Only 'name' should be required, 'age' and 'tags' are optional
        self.assertIn('name', required)
        self.assertNotIn('age', required)  # Optional[int] = None
        self.assertNotIn('tags', required)  # List[str] = None
        self.assertEqual(len(required), 1)
        
        # Check that optional parameters still have correct types
        properties = params['properties']
        self.assertEqual(properties['age']['type'], 'integer')  # Inner type of Optional[int]
        self.assertEqual(properties['tags']['type'], 'array')   # List[str]
        
    def test_generate_function_json_from_list_complex_types(self):
        """Test handling of complex type annotations."""
        functions = [create_test_function_complex_types]
        result = generate_function_json_from_list(functions)
        
        params = result[0]['function']['parameters']
        properties = params['properties']
        
        # Check complex type mapping
        self.assertEqual(properties['data']['type'], 'object')  # Dict[str, List[int]]
        self.assertEqual(properties['metadata']['type'], 'object')  # Optional[Dict[str, str]]
        
        # Check required parameters
        required = params['required']
        self.assertIn('data', required)
        self.assertNotIn('metadata', required)  # Optional parameter
        
    def test_generate_function_json_from_list_no_args(self):
        """Test function with no arguments."""
        functions = [create_test_function_no_args]
        result = generate_function_json_from_list(functions)
        
        params = result[0]['function']['parameters']
        self.assertEqual(params['type'], 'object')
        self.assertEqual(len(params['properties']), 0)
        self.assertEqual(len(params['required']), 0)
        
    def test_generate_function_json_from_list_multiple_functions(self):
        """Test JSON generation with multiple functions."""
        functions = [create_test_function_simple, create_test_function_no_args]
        result = generate_function_json_from_list(functions)
        
        self.assertEqual(len(result), 2)
        
        # Check function names
        names = [func['function']['name'] for func in result]
        self.assertIn('create_test_function_simple', names)
        self.assertIn('create_test_function_no_args', names)
        
    def test_generate_function_json_from_list_invalid_input(self):
        """Test error handling for invalid inputs."""
        # Test with non-callable object
        with self.assertRaises(ValueError) as context:
            generate_function_json_from_list(["not_a_function"])
        
        self.assertIn("not callable", str(context.exception))
        
    def test_generate_function_json_from_list_empty_list(self):
        """Test with empty function list."""
        result = generate_function_json_from_list([])
        self.assertEqual(result, [])
        
    def test_generate_function_json_from_list_function_descriptions(self):
        """Test function description extraction."""
        functions = [create_test_function_simple]
        result = generate_function_json_from_list(functions)
        
        description = result[0]['function']['description']
        self.assertIn("Simple test function", description)
        
    def test_generate_function_json_from_list_no_docstring_function(self):
        """Test function without proper docstring."""
        def function_no_docstring(x: int) -> str:
            return str(x)
        
        functions = [function_no_docstring]
        result = generate_function_json_from_list(functions)
        
        # Should still generate schema but with default description
        self.assertEqual(len(result), 1)
        description = result[0]['function']['description']
        self.assertEqual(description, "Function function_no_docstring")
        
        # Parameters should have empty descriptions when no docstring metadata
        properties = result[0]['function']['parameters']['properties']
        self.assertEqual(properties['x']['description'], "")
        
    def test_generate_function_json_schema_structure(self):
        """Test that generated schema follows OpenAI function calling format."""
        functions = [create_test_function_simple]
        result = generate_function_json_from_list(functions)
        
        schema = result[0]
        
        # Validate top-level structure
        self.assertEqual(schema['type'], 'function')
        self.assertIn('function', schema)
        
        function_def = schema['function']
        
        # Validate function definition structure
        required_fields = ['name', 'description', 'parameters', 'strict']
        for field in required_fields:
            self.assertIn(field, function_def)
        
        # Validate parameters structure
        params = function_def['parameters']
        self.assertEqual(params['type'], 'object')
        self.assertIn('properties', params)
        self.assertIn('required', params)
        self.assertIn('additionalProperties', params)
        self.assertFalse(params['additionalProperties'])
        
        # Validate parameter property structure
        for prop_name, prop_def in params['properties'].items():
            required_prop_fields = ['name', 'type', 'description']
            for field in required_prop_fields:
                self.assertIn(field, prop_def)
                
    def test_generate_function_json_all_sample_functions(self):
        """Test JSON generation with all sample functions."""
        result = generate_function_json_from_list(SAMPLE_FUNCTIONS)
        
        # Should generate schema for all functions
        self.assertEqual(len(result), len(SAMPLE_FUNCTIONS))
        
        # All should be valid function schemas
        for schema in result:
            self.assertEqual(schema['type'], 'function')
            self.assertIn('function', schema)
            self.assertTrue(schema['function']['strict'])


if __name__ == '__main__':
    unittest.main()

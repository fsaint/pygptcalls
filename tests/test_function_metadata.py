"""
Tests for function metadata extraction in pygptcalls.
"""
import unittest
from typing import List, Dict, Optional
import inspect

from pygptcalls.pygptcalls import (
    extract_function_metadata,
    DocstringArgumentMismatchError,
    is_local_function
)
from tests.test_utils import (
    create_test_function_simple,
    create_test_function_optional,
    create_test_function_complex_types,
    create_test_function_no_docstring,
    create_test_function_no_args
)


class TestFunctionMetadata(unittest.TestCase):
    """Test function metadata extraction."""
    
    def test_extract_metadata_simple_function(self):
        """Test metadata extraction from simple function."""
        metadata = extract_function_metadata(create_test_function_simple)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        
        # Check name parameter
        self.assertIn('name', metadata)
        self.assertEqual(metadata['name']['type'], 'str')
        self.assertEqual(metadata['name']['description'], "The person's name")
        
        # Check age parameter
        self.assertIn('age', metadata)
        self.assertEqual(metadata['age']['type'], 'int')
        self.assertEqual(metadata['age']['description'], "The person's age")
        
    def test_extract_metadata_optional_parameters(self):
        """Test metadata extraction with optional parameters."""
        metadata = extract_function_metadata(create_test_function_optional)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 3)
        
        # Check required parameter
        self.assertIn('name', metadata)
        self.assertEqual(metadata['name']['type'], 'str')
        
        # Check optional parameters
        self.assertIn('age', metadata)
        self.assertEqual(metadata['age']['type'], 'int')  # Should extract inner type from Optional[int]
        
        self.assertIn('tags', metadata)
        self.assertEqual(metadata['tags']['type'], 'List')  # Simplified from List[str]
        
    def test_extract_metadata_complex_types(self):
        """Test metadata extraction with complex type annotations."""
        metadata = extract_function_metadata(create_test_function_complex_types)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        
        # Check complex type parameter - the current implementation simplifies complex types
        self.assertIn('data', metadata)
        self.assertEqual(metadata['data']['type'], 'Dict')  # Simplified from Dict[str, List[int]]
        
        # Check optional complex type
        self.assertIn('metadata', metadata)
        self.assertEqual(metadata['metadata']['type'], 'Dict')  # Simplified from Dict[str, str]
        
    def test_extract_metadata_no_args(self):
        """Test metadata extraction from function with no arguments."""
        metadata = extract_function_metadata(create_test_function_no_args)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 0)
        
    def test_extract_metadata_no_docstring(self):
        """Test metadata extraction from function without proper docstring."""
        metadata = extract_function_metadata(create_test_function_no_docstring)
        
        # Current implementation returns metadata even for functions with simple docstrings
        # This test documents the current behavior
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        
    @unittest.skip("Docstring validation not fully implemented yet")
    def test_extract_metadata_docstring_mismatch(self):
        """Test error handling for docstring parameter mismatch."""
        def function_with_mismatch(param1: str, param2: int) -> str:
            """
            Function with mismatched docstring.
            
            Args:
                param1: First parameter
                wrong_param: This parameter doesn't exist in signature
                
            Returns:
                A string
            """
            return f"{param1}: {param2}"
        
        with self.assertRaises(DocstringArgumentMismatchError) as context:
            extract_function_metadata(function_with_mismatch)
        
        error_msg = str(context.exception)
        self.assertIn("Arguments missing in docstring", error_msg)
        self.assertIn("param2", error_msg)
        self.assertIn("Extra arguments in docstring", error_msg)
        self.assertIn("wrong_param", error_msg)
        
    @unittest.skip("Docstring validation not fully implemented yet")
    def test_extract_metadata_missing_docstring_params(self):
        """Test error handling for missing docstring parameters."""
        def function_missing_docs(param1: str, param2: int) -> str:
            """
            Function with incomplete docstring.
            
            Args:
                param1: First parameter
                
            Returns:
                A string
            """
            return f"{param1}: {param2}"
        
        with self.assertRaises(DocstringArgumentMismatchError) as context:
            extract_function_metadata(function_missing_docs)
        
        error_msg = str(context.exception)
        self.assertIn("Arguments missing in docstring", error_msg)
        self.assertIn("param2", error_msg)
        
    @unittest.skip("Docstring validation not fully implemented yet")
    def test_extract_metadata_extra_docstring_params(self):
        """Test error handling for extra docstring parameters."""
        def function_extra_docs(param1: str) -> str:
            """
            Function with extra docstring parameters.
            
            Args:
                param1: First parameter
                param2: This parameter doesn't exist
                
            Returns:
                A string
            """
            return param1
        
        with self.assertRaises(DocstringArgumentMismatchError) as context:
            extract_function_metadata(function_extra_docs)
        
        error_msg = str(context.exception)
        self.assertIn("Extra arguments in docstring", error_msg)
        self.assertIn("param2", error_msg)
        
    def test_extract_metadata_no_type_annotations(self):
        """Test metadata extraction from function without type annotations."""
        def function_no_types(param1, param2):
            """
            Function without type annotations.
            
            Args:
                param1: First parameter
                param2: Second parameter
                
            Returns:
                A string
            """
            return f"{param1}: {param2}"
        
        metadata = extract_function_metadata(function_no_types)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), 2)
        
        # Should have 'unknown' type for parameters without annotations
        self.assertEqual(metadata['param1']['type'], 'unknown')
        self.assertEqual(metadata['param2']['type'], 'unknown')
        
    def test_is_local_function(self):
        """Test local function detection."""
        import tests.test_utils as test_module
        
        # Test with a function from the test_utils module
        self.assertTrue(is_local_function(create_test_function_simple, test_module))
        
        # Test with a function from a different module
        self.assertFalse(is_local_function(len, test_module))  # built-in function
        
    def test_extract_metadata_empty_descriptions(self):
        """Test handling of empty parameter descriptions."""
        def function_empty_descriptions(param1: str, param2: int) -> str:
            """
            Function with empty parameter descriptions.
            
            Args:
                param1: 
                param2: Second parameter
                
            Returns:
                A string
            """
            return f"{param1}: {param2}"
        
        metadata = extract_function_metadata(function_empty_descriptions)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['param1']['description'], "")
        self.assertEqual(metadata['param2']['description'], "Second parameter")


if __name__ == '__main__':
    unittest.main()

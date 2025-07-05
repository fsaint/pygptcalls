"""
Tests for function execution in pygptcalls.
"""
import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime
import uuid

from pygptcalls.pygptcalls import execute_function
from tests.test_utils import (
    MockToolCall,
    create_test_function_simple,
    create_test_function_datetime_uuid,
    SAMPLE_DATETIME,
    SAMPLE_UUID
)


class TestFunctionExecution(unittest.TestCase):
    """Test function execution functionality."""
    
    def test_execute_function_with_functions_list_success(self):
        """Test successful function execution with functions list."""
        # Create mock tool call
        tool_call = MockToolCall(
            function_name="create_test_function_simple",
            arguments={"name": "Alice", "age": 30}
        )
        
        # Execute function
        result = execute_function(tool_call, functions=[create_test_function_simple])
        
        # Verify result structure
        self.assertEqual(result['role'], 'tool')
        self.assertEqual(result['tool_call_id'], 'test_call_id')
        
        # Verify content
        content = json.loads(result['content'])
        self.assertEqual(content, "Hello Alice, you are 30 years old")
        
    def test_execute_function_with_package_success(self):
        """Test successful function execution with package."""
        # Create mock package
        mock_package = Mock()
        mock_package.__name__ = "test_package"
        mock_package.test_function = lambda name, age: f"Package: {name}, {age}"
        
        # Create mock tool call
        tool_call = MockToolCall(
            function_name="test_function",
            arguments={"name": "Bob", "age": 25}
        )
        
        # Execute function
        result = execute_function(tool_call, package=mock_package)
        
        # Verify result
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        self.assertEqual(content, "Package: Bob, 25")
        
    def test_execute_function_not_found_in_functions_list(self):
        """Test error handling when function not found in functions list."""
        tool_call = MockToolCall(
            function_name="nonexistent_function",
            arguments={}
        )
        
        with self.assertRaises(ValueError) as context:
            execute_function(tool_call, functions=[create_test_function_simple])
        
        error_msg = str(context.exception)
        self.assertIn("Function 'nonexistent_function' not found", error_msg)
        self.assertIn("Available functions", error_msg)
        self.assertIn("create_test_function_simple", error_msg)
        
    def test_execute_function_not_found_in_package(self):
        """Test error handling when function not found in package."""
        # Create a simple mock package that doesn't have the function
        class MockPackage:
            __name__ = "test_package"
        
        mock_package = MockPackage()
        
        tool_call = MockToolCall(
            function_name="nonexistent_function",
            arguments={}
        )
        
        with self.assertRaises(AttributeError) as context:
            execute_function(tool_call, package=mock_package)
        
        error_msg = str(context.exception)
        self.assertIn("Function 'nonexistent_function' not found in package", error_msg)
        
    def test_execute_function_no_package_or_functions(self):
        """Test error handling when neither package nor functions provided."""
        tool_call = MockToolCall(
            function_name="test_function",
            arguments={}
        )
        
        with self.assertRaises(ValueError) as context:
            execute_function(tool_call)
        
        error_msg = str(context.exception)
        self.assertIn("Either 'package' or 'functions' must be provided", error_msg)
        
    def test_execute_function_with_execution_error(self):
        """Test handling of function execution errors."""
        def error_function(x: int) -> str:
            """Function that raises an error."""
            raise ValueError("Test error")
        
        tool_call = MockToolCall(
            function_name="error_function",
            arguments={"x": 42}
        )
        
        # Execute function - should not raise, but return error in content
        result = execute_function(tool_call, functions=[error_function])
        
        # Verify error is captured in response
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        self.assertIn("Error executing function error_function", content)
        self.assertIn("Test error", content)
        
    def test_execute_function_with_datetime_uuid_serialization(self):
        """Test function execution with datetime and UUID serialization."""
        tool_call = MockToolCall(
            function_name="create_test_function_datetime_uuid",
            arguments={
                "timestamp": SAMPLE_DATETIME,
                "identifier": SAMPLE_UUID
            }
        )
        
        result = execute_function(tool_call, functions=[create_test_function_datetime_uuid])
        
        # Verify serialization worked
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        
        # Should be a dict with serialized values
        self.assertIsInstance(content, dict)
        self.assertIn('timestamp', content)
        self.assertIn('id', content)
        
    def test_execute_function_with_complex_return_types(self):
        """Test function execution with complex return types."""
        def complex_return_function() -> dict:
            """Function returning complex data."""
            return {
                "data": [1, 2, 3],
                "metadata": {"key": "value"},
                "timestamp": datetime(2023, 1, 1),
                "id": uuid.UUID('12345678-1234-5678-1234-567812345678')
            }
        
        tool_call = MockToolCall(
            function_name="complex_return_function",
            arguments={}
        )
        
        result = execute_function(tool_call, functions=[complex_return_function])
        
        # Verify complex serialization
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        
        self.assertEqual(content['data'], [1, 2, 3])
        self.assertEqual(content['metadata'], {"key": "value"})
        # datetime and UUID should be serialized as strings
        self.assertEqual(content['timestamp'], '2023-01-01T00:00:00')
        self.assertEqual(content['id'], '12345678-1234-5678-1234-567812345678')
        
    def test_execute_function_with_none_return(self):
        """Test function execution with None return value."""
        def none_return_function() -> None:
            """Function returning None."""
            return None
        
        tool_call = MockToolCall(
            function_name="none_return_function",
            arguments={}
        )
        
        result = execute_function(tool_call, functions=[none_return_function])
        
        # Verify None is properly serialized
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        self.assertIsNone(content)
        
    def test_execute_function_with_empty_arguments(self):
        """Test function execution with no arguments."""
        def no_args_function() -> str:
            """Function with no arguments."""
            return "success"
        
        tool_call = MockToolCall(
            function_name="no_args_function",
            arguments={}
        )
        
        result = execute_function(tool_call, functions=[no_args_function])
        
        # Verify execution
        self.assertEqual(result['role'], 'tool')
        content = json.loads(result['content'])
        self.assertEqual(content, "success")
        
    def test_execute_function_tool_call_id_preservation(self):
        """Test that tool call ID is preserved in response."""
        custom_id = "custom_call_id_123"
        tool_call = MockToolCall(
            function_name="create_test_function_simple",
            arguments={"name": "Test", "age": 25},
            call_id=custom_id
        )
        
        result = execute_function(tool_call, functions=[create_test_function_simple])
        
        # Verify tool call ID is preserved
        self.assertEqual(result['tool_call_id'], custom_id)
        
    def test_execute_function_with_keyword_arguments(self):
        """Test function execution with keyword arguments."""
        def keyword_function(required_arg: str, optional_arg: str = "default") -> str:
            """Function with keyword arguments."""
            return f"{required_arg}:{optional_arg}"
        
        tool_call = MockToolCall(
            function_name="keyword_function",
            arguments={"required_arg": "test", "optional_arg": "custom"}
        )
        
        result = execute_function(tool_call, functions=[keyword_function])
        
        # Verify execution
        content = json.loads(result['content'])
        self.assertEqual(content, "test:custom")


if __name__ == '__main__':
    unittest.main()

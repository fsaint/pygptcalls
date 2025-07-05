"""
Test utilities and fixtures for pygptcalls testing.
"""
from typing import List, Optional, Dict, Any
from unittest.mock import Mock, MagicMock
import json
from datetime import datetime
import uuid


class MockToolCall:
    """Mock tool call object for testing."""
    
    def __init__(self, function_name: str, arguments: Dict[str, Any], call_id: str = "test_call_id"):
        self.id = call_id
        self.function = Mock()
        self.function.name = function_name
        self.function.parsed_arguments = arguments


class MockOpenAIMessage:
    """Mock OpenAI message object for testing."""
    
    def __init__(self, content: str = None, tool_calls: List[MockToolCall] = None):
        self.content = content
        self.tool_calls = tool_calls or []
        self.role = "assistant"


class MockOpenAIResponse:
    """Mock OpenAI API response for testing."""
    
    def __init__(self, message: MockOpenAIMessage, token_usage: int = 100):
        self.choices = [Mock()]
        self.choices[0].message = message
        self.usage = Mock()
        self.usage.total_tokens = token_usage


def create_test_function_simple(name: str, age: int) -> str:
    """
    Simple test function with basic parameters.
    
    Args:
        name: The person's name
        age: The person's age
        
    Returns:
        A greeting string
    """
    return f"Hello {name}, you are {age} years old"


def create_test_function_optional(name: str, age: Optional[int] = None, tags: List[str] = None) -> Dict[str, Any]:
    """
    Test function with optional parameters.
    
    Args:
        name: The person's name
        age: The person's age (optional)
        tags: List of tags (optional)
        
    Returns:
        A dictionary with the information
    """
    return {
        "name": name,
        "age": age,
        "tags": tags or []
    }


def create_test_function_complex_types(data: Dict[str, List[int]], metadata: Optional[Dict[str, str]] = None) -> bool:
    """
    Test function with complex type annotations.
    
    Args:
        data: Dictionary mapping strings to lists of integers
        metadata: Optional metadata dictionary
        
    Returns:
        Success status
    """
    return len(data) > 0


def create_test_function_no_docstring(x: int, y: str):
    """No proper docstring format."""
    return f"{x}: {y}"


def create_test_function_no_args() -> str:
    """
    Function with no arguments.
    
    Returns:
        A constant string
    """
    return "no args"


def create_test_function_datetime_uuid(timestamp: datetime, identifier: uuid.UUID) -> Dict[str, str]:
    """
    Function that uses datetime and UUID types.
    
    Args:
        timestamp: A datetime object
        identifier: A UUID object
        
    Returns:
        Dictionary with serialized values
    """
    return {
        "timestamp": timestamp.isoformat(),
        "id": str(identifier)
    }


# Test data fixtures
SAMPLE_FUNCTIONS = [
    create_test_function_simple,
    create_test_function_optional,
    create_test_function_complex_types,
    create_test_function_no_args,
    create_test_function_datetime_uuid
]

SAMPLE_DATETIME = datetime(2023, 1, 1, 12, 0, 0)
SAMPLE_UUID = uuid.UUID('12345678-1234-5678-1234-567812345678')

# Expected JSON schema patterns for validation
EXPECTED_SIMPLE_SCHEMA = {
    "type": "function",
    "function": {
        "strict": True,
        "name": "create_test_function_simple",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"name": "name", "type": "string"},
                "age": {"name": "age", "type": "integer"}
            },
            "required": ["name", "age"],
            "additionalProperties": False
        }
    }
}

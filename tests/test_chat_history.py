"""
Tests for chat history and message management in pygptcalls.
"""
import unittest
import json

from pygptcalls.pygptcalls import Message, ChatHistory


class TestMessage(unittest.TestCase):
    """Test Message model functionality."""
    
    def test_message_creation_basic(self):
        """Test basic message creation."""
        message = Message(role="user", content="Hello")
        
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertIsNone(message.tool_call_id)
        self.assertIsNone(message.tool_calls)
        
    def test_message_creation_with_tool_call_id(self):
        """Test message creation with tool call ID."""
        message = Message(
            role="tool",
            content="Function result",
            tool_call_id="call_123"
        )
        
        self.assertEqual(message.role, "tool")
        self.assertEqual(message.content, "Function result")
        self.assertEqual(message.tool_call_id, "call_123")
        self.assertIsNone(message.tool_calls)
        
    def test_message_creation_with_tool_calls(self):
        """Test message creation with tool calls."""
        tool_calls = [{"id": "call_1", "function": {"name": "test_func"}}]
        message = Message(
            role="assistant",
            content=None,
            tool_calls=tool_calls
        )
        
        self.assertEqual(message.role, "assistant")
        self.assertIsNone(message.content)
        self.assertEqual(message.tool_calls, tool_calls)
        self.assertIsNone(message.tool_call_id)
        
    def test_message_role_validation(self):
        """Test message role validation."""
        # Valid roles should work
        valid_roles = ["system", "user", "assistant", "tool"]
        for role in valid_roles:
            message = Message(role=role, content="test")
            self.assertEqual(message.role, role)
            
    def test_message_serialization(self):
        """Test message serialization to dict."""
        message = Message(
            role="user",
            content="Hello",
            tool_call_id="call_123"
        )
        
        message_dict = message.dict()
        
        self.assertEqual(message_dict['role'], "user")
        self.assertEqual(message_dict['content'], "Hello")
        self.assertEqual(message_dict['tool_call_id'], "call_123")
        self.assertIsNone(message_dict['tool_calls'])


class TestChatHistory(unittest.TestCase):
    """Test ChatHistory model functionality."""
    
    def test_chat_history_creation_empty(self):
        """Test empty chat history creation."""
        history = ChatHistory(messages=[], system_prompt="You are helpful")
        
        self.assertEqual(len(history.messages), 0)
        self.assertEqual(history.system_prompt, "You are helpful")
        
    def test_chat_history_creation_with_messages(self):
        """Test chat history creation with messages."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ]
        history = ChatHistory(messages=messages, system_prompt="Be helpful")
        
        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[0].content, "Hello")
        self.assertEqual(history.messages[1].content, "Hi there!")
        self.assertEqual(history.system_prompt, "Be helpful")
        
    def test_to_chatgpt_json_with_system_prompt(self):
        """Test conversion to ChatGPT JSON format with system prompt."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!")
        ]
        history = ChatHistory(messages=messages, system_prompt="Be helpful")
        
        json_messages = history.to_chatgpt_json()
        
        # Should have system message first, then the original messages
        self.assertEqual(len(json_messages), 3)
        
        # Check system message
        self.assertEqual(json_messages[0]['role'], "system")
        self.assertEqual(json_messages[0]['content'], "Be helpful")
        
        # Check original messages
        self.assertEqual(json_messages[1]['role'], "user")
        self.assertEqual(json_messages[1]['content'], "Hello")
        self.assertEqual(json_messages[2]['role'], "assistant")
        self.assertEqual(json_messages[2]['content'], "Hi!")
        
    def test_to_chatgpt_json_without_system_prompt(self):
        """Test conversion to ChatGPT JSON format without system prompt."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!")
        ]
        history = ChatHistory(messages=messages, system_prompt="")
        
        json_messages = history.to_chatgpt_json()
        
        # Should only have the original messages (no system message added)
        self.assertEqual(len(json_messages), 2)
        self.assertEqual(json_messages[0]['role'], "user")
        self.assertEqual(json_messages[1]['role'], "assistant")
        
    def test_to_chatgpt_json_with_tool_messages(self):
        """Test conversion with tool-related messages."""
        messages = [
            Message(role="user", content="Call a function"),
            Message(role="assistant", content=None, tool_calls=[{"id": "call_1"}]),
            Message(role="tool", content="Function result", tool_call_id="call_1"),
            Message(role="assistant", content="Here's the result")
        ]
        history = ChatHistory(messages=messages, system_prompt="System")
        
        json_messages = history.to_chatgpt_json()
        
        # Should have system + 4 messages
        self.assertEqual(len(json_messages), 5)
        
        # Check system message
        self.assertEqual(json_messages[0]['role'], "system")
        
        # Check tool call message
        self.assertEqual(json_messages[2]['role'], "assistant")
        self.assertIsNone(json_messages[2]['content'])
        self.assertIsNotNone(json_messages[2]['tool_calls'])
        
        # Check tool response message
        self.assertEqual(json_messages[3]['role'], "tool")
        self.assertEqual(json_messages[3]['content'], "Function result")
        self.assertEqual(json_messages[3]['tool_call_id'], "call_1")
        
    def test_chat_history_message_modification(self):
        """Test modifying messages in chat history."""
        messages = [Message(role="user", content="Hello")]
        history = ChatHistory(messages=messages, system_prompt="System")
        
        # Add a new message
        history.messages.append(Message(role="assistant", content="Hi!"))
        
        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[1].content, "Hi!")
        
    def test_chat_history_empty_messages(self):
        """Test chat history with empty messages list."""
        history = ChatHistory(messages=[], system_prompt="System")
        
        json_messages = history.to_chatgpt_json()
        
        # Should only have system message
        self.assertEqual(len(json_messages), 1)
        self.assertEqual(json_messages[0]['role'], "system")
        
    def test_chat_history_serialization(self):
        """Test chat history serialization."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!")
        ]
        history = ChatHistory(messages=messages, system_prompt="Be helpful")
        
        # Should be able to serialize to dict
        history_dict = history.dict()
        
        self.assertIn('messages', history_dict)
        self.assertIn('system_prompt', history_dict)
        self.assertEqual(len(history_dict['messages']), 2)
        self.assertEqual(history_dict['system_prompt'], "Be helpful")
        
    def test_message_with_complex_tool_calls(self):
        """Test message with complex tool call structure."""
        complex_tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "San Francisco"}'
                }
            },
            {
                "id": "call_2", 
                "type": "function",
                "function": {
                    "name": "get_time",
                    "arguments": '{"timezone": "UTC"}'
                }
            }
        ]
        
        message = Message(
            role="assistant",
            content="I'll get the weather and time for you.",
            tool_calls=complex_tool_calls
        )
        
        self.assertEqual(len(message.tool_calls), 2)
        self.assertEqual(message.tool_calls[0]["function"]["name"], "get_weather")
        self.assertEqual(message.tool_calls[1]["function"]["name"], "get_time")


if __name__ == '__main__':
    unittest.main()

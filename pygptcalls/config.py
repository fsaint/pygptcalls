"""
Configuration classes for pygptcalls library.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GPTCallConfig:
    """
    Configuration class for GPT function calling.
    
    Attributes:
        model: The OpenAI model to use for function calling.
        debug: Whether to enable debug mode with verbose output.
        api_key: The OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        system_prompt: The system prompt to use for the conversation.
        max_iterations: Maximum number of function call iterations to prevent infinite loops.
        timeout: Timeout in seconds for individual function calls.
    """
    model: str = "gpt-4o-mini"
    debug: bool = False
    api_key: Optional[str] = None
    system_prompt: str = "You are a helpful assistant."
    max_iterations: int = 10
    timeout: int = 30

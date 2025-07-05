import inspect
import json
from openai import OpenAI
import os
import sys
import re
from typing import Dict, Any, Callable, List, Optional, Union
from datetime import datetime
import uuid
from typing import List, Literal, Dict, get_origin, get_args
from pydantic import BaseModel
import docstring_parser

class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None
    tool_call_id: str | None = None
    tool_calls: Any | None = None

class ChatHistory(BaseModel):
    messages: List[Message]
    system_prompt: str

    def to_chatgpt_json(self) -> List[Dict]:
        chat_messages = self.messages.copy()
        if self.system_prompt:
            chat_messages.insert(0, Message(role="system", content=self.system_prompt))
        return [message.dict() for message in chat_messages]


def is_local_function(member, module) -> bool:
    """
    Check if a member is a function defined in the current module.
    
    Args:
        member: The member to check.
        module: The module to check against.
        
    Returns:
        bool: True if the member is a function defined in the current module.
    """
    return inspect.isfunction(member) and member.__module__ == module.__name__


def is_optional_type(typ) -> bool:
    return get_origin(typ) is Union and type(None) in get_args(typ)


def map_python_type_to_json_type(python_type: type) -> str:
    '''
    Maps Python types to corresponding JSON type field values.

    Args:
        python_type (type): The Python type to convert.

    Returns:
        str: Corresponding JSON type as a string.
    '''
    if is_optional_type(python_type):
        python_type = python_type.__args__[0]
    origin = get_origin(python_type) or python_type
    type_mapping = {
        str: 'string',
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        dict: 'object',
        list: 'array',
        type(None): 'null'
    }

    return type_mapping.get(origin, 'string')


class DocstringArgumentMismatchError(Exception):
    '''
    Exception raised when there is a mismatch between
    function arguments as per the docstring and actual parameters.
    '''
    pass


def number_of_arguments(func):
    # Get the function's signature
    sig = inspect.signature(func)

    # Get the number of arguments
    return len([
        param for param in sig.parameters.values() 
        if param.default == inspect.Parameter.empty and param.kind in 
        (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY)
    ]) 

def extract_function_metadata(function: Callable) -> Optional[Dict[str, Dict[str, str]]]:
    """
    Extracts metadata from a function's signature and docstring. Types are taken from the signature,
    while descriptions are taken from the docstring.

    Args:
        function (Callable): The function to extract metadata from.

    Returns:
        Optional[Dict[str, Dict[str, str]]]: A dictionary mapping argument names to
        their type and description, or None if no docstring is found.

    Raises:
        DocstringArgumentMismatchError: If the docstring is improperly formatted.
    """
    docstring = inspect.getdoc(function)
    if not docstring:
        return None

    # Get parameter types from function signature
    signature = inspect.signature(function)
    
    # Parse docstring for descriptions
    parsed_doc = docstring_parser.parse(docstring)
    
    # Create a mapping of parameter names to their descriptions from docstring
    param_descriptions = {
        param.arg_name: param.description.strip() if param.description else ""
        for param in parsed_doc.params
    }
    
    # Build args_metadata primarily from signature, with descriptions from docstring
    args_metadata = {}
    for param_name, param in signature.parameters.items():
        param_type = "unknown"
        annotation = param.annotation
        
        # If the type is optional, use the inner type
        if param.annotation != inspect.Parameter.empty:
            if is_optional_type(param.annotation):
                # Get the inner type (first non-None type)
                inner_types = [t for t in get_args(param.annotation) if t is not type(None)]
                if inner_types:
                    annotation = inner_types[0]
            
            if hasattr(annotation, "__name__"):
                param_type = annotation.__name__
            else:
                # Handle complex types like Union, List, etc.
                param_type = str(annotation).replace("typing.", "")
                
        args_metadata[param_name] = {
            "type": param_type,
            "description": param_descriptions.get(param_name, "")
        }

    # Validate function signature matches extracted docstring arguments
    function_params = set(inspect.signature(function).parameters.keys())
    docstring_args = set(args_metadata.keys())

    if function_params != docstring_args:
        missing_in_docstring = function_params - docstring_args
        extra_in_docstring = docstring_args - function_params
        error_msg = []

        if missing_in_docstring:
            error_msg.append(f"Arguments missing in docstring: {', '.join(missing_in_docstring)}")
        if extra_in_docstring:
            error_msg.append(f"Extra arguments in docstring: {', '.join(extra_in_docstring)}")

        raise DocstringArgumentMismatchError(". ".join(error_msg))

    #print(args_metadata)
    return args_metadata

def generate_function_json(module) -> str:
    '''
    Generates a JSON description of functions in a given Python package/module,
    suitable for function calling in the ChatGPT API.

    Args:
        module: The module to extract functions from.

    Returns:
        str: A JSON representation of functions.
    '''
    functions = []
    for name, obj in inspect.getmembers(module, lambda member: is_local_function(member, module)):
        sig = inspect.signature(obj)
        params = []
        docstring = extract_function_metadata(obj)
        required = []
        for param in sig.parameters.values():
            param_description = {
                "name": param.name,
                "type": "string" if param.annotation == inspect.Parameter.empty else map_python_type_to_json_type(param.annotation),
                "description": docstring[param.name]['description'],
            }
            # Only add to required if parameter has no default value and is not optional
            if param.default == inspect.Parameter.empty and not is_optional_type(param.annotation):
                required.append(param.name)
            params.append(param_description)
        functions.append({
            "type": "function",
            "function":{
                "strict": True,
                "name": name,
                "description": obj.__doc__.strip() if obj.__doc__ else f"Function {name}",
                "parameters": {
                    "type": "object",
                    "properties": {param['name']: param for param in params},
                    "required": required,
                    "additionalProperties": False
                },
            }
        })
    return functions

from typing import List, Callable

def generate_function_json_from_list(functions_list: List[Callable]) -> str:
    '''
    Generates a JSON description of functions from a given list of functions,
    suitable for function calling in the ChatGPT API.

    Args:
        functions_list: A list of function objects to describe.

    Returns:
        str: A JSON representation of the functions.
    '''
    functions = []

    for obj in functions_list:
        if not callable(obj):
            raise ValueError(f"Object {obj} is not callable. Ensure all elements in the list are functions.")

        name = obj.__name__
        sig = inspect.signature(obj)
        params = []
        docstring = extract_function_metadata(obj)  # Ensure this helper is defined elsewhere
        required = []

        for param in sig.parameters.values():
            param_description = {
                "name": param.name,
                "type": "string" if param.annotation == inspect.Parameter.empty else map_python_type_to_json_type(param.annotation),
                "description": docstring.get(param.name, {}).get('description', f"Parameter {param.name}") if docstring else "",
            }
            # Only add to required if parameter has no default value and is not optional
            if param.default == inspect.Parameter.empty and not is_optional_type(param.annotation):
                required.append(param.name)
            params.append(param_description)
        
        functions.append({
            "type": "function",
            "function": {
                "strict": True,
                "name": name,
                "description": obj.__doc__.strip() if obj.__doc__ else f"Function {name}",
                "parameters": {
                    "type": "object",
                    "properties": {param['name']: param for param in params},
                    "required": required,
                    "additionalProperties": False
                },
            }
        })

    return functions

def custom_serializer(obj):
    '''
    Custom function for json serialization of non-standard types.
    '''
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    if isinstance(obj, uuid.UUID):
        return str(obj)  # Convert UUID to a string
    raise TypeError(f"Type {type(obj)} not serializable")

def execute_function(tool_call: Any, package: Any = None, functions: List[Callable] = None) -> dict:
    '''
    Executes a function from a given package using arguments
    provided in a tool call.

    Args:
        package: The package containing the function to execute.
        tool_call: The tool call object containing the function name and arguments.
        functions: List of functions to search for the function to execute.

    Returns:
        dict: The response from the executed function.
        
    Raises:
        AttributeError: If the function is not found in the package.
        ValueError: If the function is not found in the functions list.
    '''
    arguments = tool_call.function.parsed_arguments
    function = None
    
    if package:
        try:
            function = getattr(package, tool_call.function.name)
        except AttributeError:
            raise AttributeError(f"Function '{tool_call.function.name}' not found in package {package.__name__}")
    elif functions:
        for func in functions:
            if func.__name__ == tool_call.function.name:
                function = func
                break
        if function is None:
            available_functions = [f.__name__ for f in functions]
            raise ValueError(f"Function '{tool_call.function.name}' not found in functions list. Available functions: {available_functions}")
    else:
        raise ValueError("Either 'package' or 'functions' must be provided")
            
    try:
        response = function(**arguments)
    except Exception as e:
        # Return error as tool response instead of crashing
        response = f"Error executing function {tool_call.function.name}: {str(e)}"
    
    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(response, default=custom_serializer),
        "tool_call_id": tool_call.id
    }
    return function_call_result_message


def format_output(client, text: str, response_format) -> Any:
    """
    Formats the input text using the specified response format.
    
    Args:
        client: The OpenAI client instance.
        text: The input text to format.
        response_format: The desired response format.
        
    Returns:
        The formatted response.
    """
    system = """
        Your job is to transform the input text into a formatted output.
    """
    response = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system", 
                "content": system
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_format=response_format,
        model="gpt-4o-mini",
    )
    return response


def execute_openai_with_tools(client, tools_json: dict, chat_history: ChatHistory | None, package: Optional[Any] = None, messages: List[dict] = [], debug: bool = False) -> tuple:
    '''
    Sends a prompt to the OpenAI API with specified tools and returns the response.

    Args:
        prompt (str): The user prompt to send to the API.
        tools_json (dict): The tools available for the API to call.
        api_key (Optional[str]): The OpenAI API key.
        package (Optional[Any]): The package containing the functions to execute.
        messages (List[dict]): Previous messages in the conversation.
        debug (bool): Enables debug mode.

    Returns:
        tuple: The API response message and tool calls.
    '''
    messages = chat_history.to_chatgpt_json()
    try:
        response =  client.beta.chat.completions.parse(
                messages=messages,
            model="gpt-4o-mini",#gpt-4o-mini
            tools=tools_json,
        )
        
        if debug:
            print(f"\033[1mTokens used\033[0m: {response.usage.total_tokens}")
        return (response.choices[0].message, response.choices[0].message.tool_calls)
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")


def gptcall(prompt: str, package = None, api_key: Optional[str] = None, debug: bool = False, functions: List[Callable] = None, system = "You are a helpful assistant.", response_format = None, max_iterations: int = 10) -> Optional[str]:
    '''
    Calls a function from the given package based on the user prompt and
    manages tool calls.

    Args:
        prompt (str): The user prompt to process.
        package: The package containing functions to call.
        api_key (Optional[str]): The OpenAI API key.
        debug (bool): Enables debug mode.
        functions (List[Callable]): List of functions to make available.
        system (str): System prompt for the conversation.
        response_format: Response format for structured output.
        max_iterations (int): Maximum number of function call iterations to prevent infinite loops.

    Returns:
        Optional[str]: The content of the final response or None.
    '''
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key,
    )
    if package:
        tools = generate_function_json(package)
    elif functions:
        tools = generate_function_json_from_list(functions)
    else:
        tools = []
        
    chat_history = ChatHistory(
        messages=[Message(role="user", content=prompt)],
        system_prompt=system
    )
    
    iteration_count = 0
    while iteration_count < max_iterations:
        iteration_count += 1
        
        message, calls = execute_openai_with_tools(client, chat_history=chat_history,  tools_json=tools, package = package,  debug = debug)
        if message.content is not None:
            if response_format:
                return format_output(client, message.content, response_format)
            else:
                return message.content
                
        # Add assistant message with tool calls to history
        chat_history.messages.append(Message(
            role=message.role, 
            content=message.content, 
            tool_calls=[json.loads(x.model_dump_json()) for x in message.tool_calls] if message.tool_calls else None
        ))
        
        for tool_call in calls:
            if debug:
                args = ",".join([f"{key}='{value}'" for key, value in tool_call.function.parsed_arguments.items()])
                print(f"\033[1mFunction call\033[0m:{tool_call.function.name}({args})")
            response = execute_function(tool_call, package = package, functions=functions)
            chat_history.messages.append(Message(
                role=response['role'], 
                content=response['content'], 
                tool_call_id=response['tool_call_id']
            ))
    
    # If we reach max iterations, return a message indicating this
    return f"Maximum iterations ({max_iterations}) reached. The conversation may be stuck in a loop."
def gptcall_chat(history: ChatHistory, package = None, api_key: Optional[str] = None, debug: bool = False, functions: List[Callable] = None, response_format = None) -> Optional[str]:
    '''
    Calls a function from the given package based on the user prompt and
    manages tool calls.

    Args:
        package: The package containing functions to call.
        prompt (str): The user prompt to process.
        api_key (Optional[str]): The OpenAI API key.
        confirm_calls (bool): Whether to confirm before executing calls.
        debug (bool): Enables debug mode.

    Returns:
        Optional[str]: The content of the final response or None.
    '''
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key,
    )
    if package:
        tools = generate_function_json(package)
    elif functions:
        tools = generate_function_json_from_list(functions)
    else:
        tools = []
    #if debug:
    #    print("tools json")
    #    print(json.dumps(tools, indent=True))
    
    while True:
        message, calls = execute_openai_with_tools(client, chat_history=history, tools_json=tools, package = package, debug = debug)
        if message.content is not None:
            if response_format:
                return format_output(client, message.content, response_format)
            else:
                return message.content
        
        
        history.messages.append(Message(role=message.role, content=message.content, tool_calls = [json.loads(x.model_dump_json()) for x in message.tool_calls]))
        
        for tool_call in calls:
            if debug:
                args = ",".join([f"{key}='{value}'" for key, value in tool_call.function.parsed_arguments.items()])
                print(f"\033[1mFunction call\033[0m:{tool_call.function.name}({args})")
            response = execute_function(tool_call, package = package, functions=functions)
            history.messages.append(Message(role = response['role'], content = response['content'], tool_call_id = response['tool_call_id']))

if __name__ == '__main__':
    pass

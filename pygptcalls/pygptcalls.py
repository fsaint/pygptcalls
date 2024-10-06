import inspect
import json
from openai import OpenAI
import os
import sys
import re
from typing import Dict, Any, Callable, List, Optional



# Get all functions in the current module
def is_local_function(member, module):
    # Checspect.isfunction(membk if the member is a function and is defined in the current module
    if inspect.isfunction(member):
        print(member)
        print(member.__module__)
    return inspect.isfunction(member) and member.__module__ == module.__name__



def map_python_type_to_json_type(python_type: type) -> str:
    '''
    Maps Python types to corresponding JSON type field values.

    Args:
        python_type (type): The Python type to convert.

    Returns:
        str: Corresponding JSON type as a string.
    '''
    type_mapping = {
        str: 'string',
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        dict: 'object',
        list: 'array',
        type(None): 'null'
    }

    return type_mapping.get(python_type, 'string')


class DocstringArgumentMismatchError(Exception):
    '''
    Exception raised when there is a mismatch between
    function arguments as per the docstring and actual parameters.
    '''
    pass


def extract_function_metadata(function: Callable) -> Dict[str, Dict[str, str]]:
    '''
    Extracts metadata from a function's docstring, including
    argument types and descriptions.

    Args:
        function (Callable): The function to extract metadata from.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary mapping argument names to
        their type and description.

    Raises:
        DocstringArgumentMismatchError: If the docstring is improperly formatted.
    '''
    docstring = inspect.getdoc(function)
    print(docstring)
    if not docstring:
        raise DocstringArgumentMismatchError(f"Function {function} has no docstring")

    args_pattern = r'Args:\s*(.*?)(?=\n\s*(Returns|Raises|$))'
    match = re.search(args_pattern, docstring, re.DOTALL)
    if not match:
        raise DocstringArgumentMismatchError(f"No 'Args' section found in docstring function {function}")

    args_description = match.group(1)
    arg_pattern = r'(\w+)\s*\(([^)]+)\):\s*(.*?)(?=\n\s*\w+\s*\(|$)'
    args_metadata = {}
    for arg in re.finditer(arg_pattern, args_description, re.DOTALL):
        arg_name = arg.group(1)
        arg_type = arg.group(2)
        arg_desc = arg.group(3).strip()
        args_metadata[arg_name] = {
            "type": arg_type,
            "description": arg_desc
        }

    signature = inspect.signature(function)
    function_params = list(signature.parameters.keys())
    docstring_args = list(args_metadata.keys())
    if set(docstring_args) != set(function_params):
        missing_in_docstring = set(function_params) - set(docstring_args)
        extra_in_docstring = set(docstring_args) - set(function_params)
        error_msg = []
        if missing_in_docstring:
            error_msg.append(f"Arguments missing in docstring: {', '.join(missing_in_docstring)}")
        if extra_in_docstring:
            error_msg.append(f"Extra arguments in docstring: {', '.join(extra_in_docstring)}")
        raise DocstringArgumentMismatchError(". ".join(error_msg))

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
        print(docstring)
        required = []
        for param in sig.parameters.values():
            param_description = {
                "name": param.name,
                "type": "string" if param.annotation == inspect.Parameter.empty else map_python_type_to_json_type(param.annotation),
                "description": docstring[param.name]['description'],
            }
            if param.default == inspect.Parameter.empty:
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


def execute_function(package: Any, tool_call: Any) -> dict:
    '''
    Executes a function from a given package using arguments
    provided in a tool call.

    Args:
        package: The package containing the function to execute.
        tool_call: The tool call object containing the function name and arguments.

    Returns:
        dict: The response from the executed function.
    '''
    arguments = tool_call.function.parsed_arguments
    function = getattr(package, tool_call.function.name)
    response = function(**arguments)
    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(response),
        "tool_call_id": tool_call.id
    }
    return function_call_result_message


def execute_openai_with_tools(prompt: str, tools_json: dict, api_key: Optional[str] = None, package: Optional[Any] = None, messages: List[dict] = [], debug: bool = False) -> tuple:
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
    client = OpenAI(
        api_key=api_key,
    )
    try:
        response =  client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system", 
                    "content":  "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ] + messages,
            model="gpt-4o-mini",#gpt-4o-mini
            tools=tools_json
        )
        if debug:
            print(f"\033[1mTokens used\033[0m: {response.usage.total_tokens}")
        return (response.choices[0].message, response.choices[0].message.tool_calls)
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")


def gptcall(package, prompt: str, api_key: Optional[str] = None, confirm_calls: bool = False, debug: bool = False) -> Optional[str]:
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
    tools = generate_function_json(package)
    if debug:
        print("tools json")
        print(json.dumps(tools, indent=True))
    responses = []
    while True:
        message, calls = execute_openai_with_tools(prompt, tools_json=tools, api_key= api_key, package = package, messages = responses, debug = debug)
        if message.content is not None:
            return message.content
        responses.append(message)
        for tool_call in calls:
            if debug:
                args = ",".join([f"{key}='{value}'" for key, value in tool_call.function.parsed_arguments.items()])
                print(f"\033[1mFunction call\033[0m:{tool_call.function.name}({args})")
            response = execute_function(package, tool_call)
            responses.append(response)

if __name__ == '__main__':
    import example_tools

    prompt = "Find all the mentions of people in the files in directory 'people'"
    gptcall(call_tool(example_tools, prompt))

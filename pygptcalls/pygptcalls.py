import inspect
import json
from openai import OpenAI
import os
import re
from typing import Dict, Any



def map_python_type_to_json_type(python_type) -> str:
    '''
    Maps Python types to corresponding JSON type field values.
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

    # Return the mapped type, or 'string' as a default if not found
    return type_mapping.get(python_type, 'string')


class DocstringArgumentMismatchError(Exception):
    pass

def extract_function_metadata(function) -> Dict[str, Dict[str, str]]:
    # Get the docstring of the function
    docstring = inspect.getdoc(function)
    if not docstring:
        raise DocstringArgumentMismatchError("Function has no docstring")

    # Extract arguments section from the docstring
    args_pattern = r'Args:\s*(.*?)(?=\n\s*(Returns|Raises|$))'
    match = re.search(args_pattern, docstring, re.DOTALL)
    if not match:
        raise DocstringArgumentMismatchError("No 'Args' section found in docstring")

    args_description = match.group(1)

    # Extract each argument and its description
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

    # Get actual function parameters
    signature = inspect.signature(function)
    function_params = list(signature.parameters.keys())

    # Compare docstring arguments with function parameters
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
    '''
    functions = []
    
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        # Extract the function signature
        sig = inspect.signature(obj)
        params = []
        
        # Iterate through the parameters
        required = []
        for param in sig.parameters.values():
            param_description = {
                "name": param.name,
                "type": "string" if param.annotation == inspect.Parameter.empty else map_python_type_to_json_type(param.annotation),
                "description": f"Parameter {param.name}",
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
    
    # Convert to JSON format
    return functions

def execute_function(package, tool_call):
    arguments = tool_call.function.parsed_arguments
    function = getattr(package, tool_call.function.name)
    response = function(**arguments)
    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(response),
        "tool_call_id": tool_call.id
    }
    return function_call_result_message

def execute_openai_with_tools(prompt: str, tools_json: dict, api_key: str = None, package =  None, messages = []):
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
        try:
            print("Tool Calls:", response.choices[0].message.tool_calls)
        except:
            print("Failed")
        #return response.choices[0].message.content
        print(f"Tokens used: {response.usage.total_tokens}")
        return (response.choices[0].message, response.choices[0].message.tool_calls)
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")


def gptcall(package, prompt, api_key = None):
    # Example usage with a built-in module like os
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    tools = generate_function_json(package)
    print(json.dumps(tools, indent=True))
    responses = []
    while True:
        #print("Iteration ------")
        message, calls = execute_openai_with_tools(prompt, tools_json=tools, api_key= api_key, package = example_tools, messages = responses)
        #print(message)
        if message.content is not None:
            return message.content
        responses.append(message)
        for tool_call in calls:
            response = execute_function(example_tools, tool_call)
            responses.append(response)
        print(responses)
#print(r)
#print(tools)

if __name__ == '__main__':
    import example_tools

    prompt = "Find all the mentions of people in the files in directory 'people'"
    gptcall(call_tool(example_tools, prompt))



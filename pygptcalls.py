import inspect
import json
from openai import OpenAI
import os

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
        for tool_call in calls:
            response = execute_function(example_tools, tool_call)
            responses.append(message)
            responses.append(response)
        print(responses)
#print(r)
#print(tools)

if __name__ == '__main__':
    import example_tools

    prompt = "Find all the mentions of people in the files in directory 'people'"
    gptcall(call_tool(example_tools, prompt))



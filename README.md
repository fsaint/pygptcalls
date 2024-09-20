# ChatGPT Function Calling Python Library

Write your functions in a package, call the chatgpt api, and GPTCal library handles all the internal details.

```python
from pygptcall import gptcall 
# your functions in an imported package
import example_tools

prompt = "Find all the mentions of people in the files in directory 'people'"
gptcall(call_tool(example_tools, prompt))
'''
Output:
In the provided text from "file1.txt", there are specific mentions of people or characters:

1. **Ishmael** - The narrator who starts the text with "Call me Ishmael."
2. **Cato** - Reference to Cato as a philosophical figure who throws himself upon his sword.

These are the recognizable mentions of people within the excerpt. If you need any further analysis or additional data from other files or context, feel free to ask!
'''
```


⚠️ **Warning:** Don't pass nuclear launch functions or deadly robot command functions. 

The **ChatGPT Function Calling Python Library** provides an easy-to-use interface for integrating Python functions with OpenAI's Function Calling API. It allows developers to interact with ChatGPT's conversational interface and call Python functions dynamically based on user inputs.

1. Define a few functions that you want chatgpt to be able to call. Put them in a separate file or package. Use docstring to provide information on what the function does. For exmaple in a file `example_tools.py` we can have basic file manipulation functions for your local filesystem.

```python
import os
from typing import List

def list_files(path: str) -> List[str]:
    '''
    List files in a given path
    '''
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except FileNotFoundError:
        print(f"The path {path} does not exist.")
        return []

def read_file(path: str) -> str:
    '''
    Read the contents of a file in the given path and return as a string
    '''
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file at {path} does not exist.")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return ""


def over_write_file(content: str, path: str):
    '''
    Overwrite the file at the given path with the provided string content.
    '''
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
```

2. Call the the prompt
   
```python
from pygptcall import gptcall 
import example_tools

prompt = "Find all the mentions of people in the files in directory 'people'"
gptcall(call_tool(example_tools, prompt))
```

In the example, the library will call the chatgpt api and execute the local calls until a response is generated. In this case I added the first chapter of moby dick to the `people` directory. The output was

```
In the provided text from "file1.txt", there are specific mentions of people or characters:

1. **Ishmael** - The narrator who starts the text with "Call me Ishmael."
2. **Cato** - Reference to Cato as a philosophical figure who throws himself upon his sword.

These are the recognizable mentions of people within the excerpt. If you need any further analysis or additional data from other files or context, feel free to ask!
```


** Run unit tests
```
python -m unittest discover -s tests
```

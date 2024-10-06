# ChatGPT Function Calling Python Library

Write your functions in a package, call the chatgpt api, and GPTCall library handles all the internal details.

```python
from pygptcalls import gptcall
import examples.file_ops as file_ops

if __name__ == '__main__':
    prompt = "In the directory pygptcalls read .py files and criticise the code. Use a snarky tone and make jokes. Save the output in a file out.txt with the file where you found the code and the approximate line."
    gptcall(file_ops, prompt, debug = True)
'''
Critique of pygptcalls/__init__.py
-------------------------------------------------------
1. This is a module initializer, and honestly, it seems like a glorified import list. Did we really need to split everything into modules, or are we just trying to impress someone with our directory structure?

Critique of pygptcalls/pygptcalls.py
-------------------------------------------------------
1. Line 6: Map Python Type to JSON Type? Let's hope this function doesn't end up in a mapping mess like my GPS does when I try to find a coffee shop.

2. Line 15: There's a default value for 'type'. Such a clever catch-all! Too bad it mainly catches confusion instead of errors.

3. Lines 41-47: Docstring Argument Mismatch Error... Or as I like to call it, the classic "This function is not what I asked for" error. Nothing like a bit of humor in failing to match arguments!

4. Lines 61-72: You know, traversing function parameters should really come with a map. How many more regex patterns do we need to extract what we want? At this point, it feels like a treasure hunt!

5. Line 84: Finally, we convert to JSON! The moment of truth. Just remember, folks, no one said JSON is not a little bit of a monster.

6. Line 95-107: Oh look, we have OpenAI managing our lives again. Does anyone else feel like we're just one step away from Skynet?

7. Last line: If this script were a person, it would be the one that always needs to check if it needs to re-import everything on every run!

Summary:
Your code is like a rollercoaster ride: full of loops, risky turns, and in the end, you just want your $10 back. Remember, less is sometimes more, and try to keep your function call parameters a tad less like an old-school phonebook.

And guess what? I saved it all into a file called 'out.txt'. Have at it!
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
from pygptcalls import gptcall 
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

## Install
This library is maturing. Install with caution
```
pip install git+https://github.com/fsaint/pygptcalls
```


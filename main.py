from pygptcalls import gptcall
import pygptcalls.tools.file_ops as file_ops
from pygptcalls.tools.file_ops import find_files_with_extension, read_file_to_string, write_string_to_file, append_to_file
from pydantic import BaseModel
from typing import List
class Person(BaseModel):
    name: str
    role: str
    file: str

class Persons(BaseModel):
    persons: List[Person]

def test_structured():
    prompt = """
        Read all files in the people directory. Create a list of all the peolpe mentioned and their roles. in the stories. 
    """
    r = gptcall(package=file_ops, prompt=prompt, debug = True,response_format=Persons)
    print(r)
def base_test():
    prompt = "In the directory pygptcalls read .py files and criticise the code. Use a snarky tone and make jokes. Save the output in a file out.txt with the file where you found the code and the approximate line."
    gptcall(package=file_ops, prompt=prompt, debug = True)
    
if __name__ == '__main__':
    #gptcall(functions=[find_files_with_extension, read_file_to_string, write_string_to_file], prompt=prompt, debug = True)
    test_structured()
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

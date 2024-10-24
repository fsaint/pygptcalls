import os
from typing import List

def find_files_with_extension(root_dir: str, extension: str) -> List[str]:
    """
    Recursively find files from a root directory with a specific extension.
    
    Args:
        root_dir (str): The root directory to search.
        extension (str): The file extension to look for (e.g., '.txt').
    
    Returns:
        List[str]: A list of file paths matching the given extension.
    """
    matched_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(extension):
                matched_files.append(os.path.join(dirpath, filename))
    return matched_files

def read_file_to_string(file_path: str) -> str:
    """
    Read a file from a specified path and return its contents as a string.
    
    Args:
        file_path (str): The path to the file to read.
    
    Returns:
        str: The contents of the file as a string.
    """
    with open(file_path, 'r') as file:
        return file.read()

def write_string_to_file(file_path: str, content: str) -> None:
    """
    Write a string to a file at a specified path.

    Args:
        file_path (str): The path to the file to write.
        content (str): The string content to write into the file.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        file.write(content)

def append_to_file(text: str, file_path: str) -> None:
    """
    Appends a given string to a file. If the file does not exist, it creates the file.

    Args:
        text (str): The text to append to the file.
        file_path (str): The path to the file.

    Returns:
        None
    """
    with open(file_path, 'a') as file:
        file.write(text + '\n')

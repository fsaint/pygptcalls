from pygptcalls import gptcall
import pygptcalls.tools.file_ops as file_ops
from pygptcalls.tools.file_ops import find_files_with_extension, read_file_to_string, write_string_to_file, append_to_file
if __name__ == '__main__':
    prompt = "In the directory pygptcalls read .py files and criticise the code. Use a snarky tone and make jokes. Save the output in a file out.txt with the file where you found the code and the approximate line."
    gptcall(package=file_ops, prompt=prompt, debug = True)
    #gptcall(functions=[find_files_with_extension, read_file_to_string, write_string_to_file], prompt=prompt, debug = True)

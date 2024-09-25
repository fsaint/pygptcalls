from pygptcalls import gptcall
import examples.file_ops as file_ops

if __name__ == '__main__':
    prompt = "In the directory pygptcalls read .py files and criticise the code. Use a snarky tone and make jokes. Save the output in a file out.txt with the file where you found the code and the approximate line."
    gptcall(file_ops, prompt, debug = True)

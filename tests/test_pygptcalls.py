import unittest
from pygptcalls import generate_function_json, extract_function_metadata, DocstringArgumentMismatchError
import tests.sample_package as sample_package
import inspect
import json
class TestGenerateFunction(unittest.TestCase):
    def test_some_function(self):
        tools = generate_function_json(sample_package)
        #print(json.dumps(tools, indent=True))
        self.assertEqual(len(tools), 2)

    def test_extract_function_metadata(self):
        r  = extract_function_metadata(sample_package.function_with_three_arguments)
        self.assertEqual(len(r), len(inspect.signature(sample_package.function_with_three_arguments).parameters))

    def test_bad_function(self):
        try:
            r  = extract_function_metadata(sample_package.bad_function1)
            self.fail()
        except DocstringArgumentMismatchError:
            pass
        except:
            self.fail()
        
    
if __name__ == '__main__':
    unittest.main()

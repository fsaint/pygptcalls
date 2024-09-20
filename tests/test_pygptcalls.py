import unittest
from pygptcalls import generate_function_json
import tests.sample_package as sample_package
import json
class TestGenerateFunction(unittest.TestCase):
    def test_some_function(self):
        tools = generate_function_json(sample_package)
        #print(json.dumps(tools, indent=True))
        self.assertEqual(len(tools), 1)

if __name__ == '__main__':
    unittest.main()

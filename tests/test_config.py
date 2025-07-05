"""
Tests for configuration system in pygptcalls.
"""
import unittest

from pygptcalls.config import GPTCallConfig


class TestGPTCallConfig(unittest.TestCase):
    """Test configuration class functionality."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = GPTCallConfig()
        
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertFalse(config.debug)
        self.assertIsNone(config.api_key)
        self.assertEqual(config.system_prompt, "You are a helpful assistant.")
        self.assertEqual(config.max_iterations, 10)
        self.assertEqual(config.timeout, 30)
        
    def test_custom_values(self):
        """Test configuration with custom values."""
        config = GPTCallConfig(
            model="gpt-4",
            debug=True,
            api_key="test_key",
            system_prompt="Custom prompt",
            max_iterations=5,
            timeout=60
        )
        
        self.assertEqual(config.model, "gpt-4")
        self.assertTrue(config.debug)
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.system_prompt, "Custom prompt")
        self.assertEqual(config.max_iterations, 5)
        self.assertEqual(config.timeout, 60)
        
    def test_partial_custom_values(self):
        """Test configuration with partial custom values."""
        config = GPTCallConfig(
            debug=True,
            max_iterations=15
        )
        
        # Custom values
        self.assertTrue(config.debug)
        self.assertEqual(config.max_iterations, 15)
        
        # Default values should remain
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertIsNone(config.api_key)
        self.assertEqual(config.system_prompt, "You are a helpful assistant.")
        self.assertEqual(config.timeout, 30)
        
    def test_config_immutability_after_creation(self):
        """Test that config values can be modified after creation."""
        config = GPTCallConfig()
        
        # Should be able to modify values (dataclass is mutable by default)
        config.debug = True
        config.max_iterations = 20
        
        self.assertTrue(config.debug)
        self.assertEqual(config.max_iterations, 20)
        
    def test_config_type_validation(self):
        """Test that config accepts correct types."""
        # This should work without errors
        config = GPTCallConfig(
            model="gpt-4",
            debug=False,
            api_key=None,
            system_prompt="Test",
            max_iterations=5,
            timeout=30
        )
        
        self.assertIsInstance(config.model, str)
        self.assertIsInstance(config.debug, bool)
        self.assertIsInstance(config.max_iterations, int)
        self.assertIsInstance(config.timeout, int)
        
    def test_config_string_representation(self):
        """Test string representation of config."""
        config = GPTCallConfig(debug=True, max_iterations=5)
        
        str_repr = str(config)
        self.assertIn("GPTCallConfig", str_repr)
        self.assertIn("debug=True", str_repr)
        self.assertIn("max_iterations=5", str_repr)
        
    def test_config_equality(self):
        """Test config equality comparison."""
        config1 = GPTCallConfig(debug=True, max_iterations=5)
        config2 = GPTCallConfig(debug=True, max_iterations=5)
        config3 = GPTCallConfig(debug=False, max_iterations=5)
        
        self.assertEqual(config1, config2)
        self.assertNotEqual(config1, config3)
        
    def test_config_copy(self):
        """Test config copying."""
        import copy
        
        original = GPTCallConfig(debug=True, api_key="test")
        copied = copy.copy(original)
        deep_copied = copy.deepcopy(original)
        
        # Should be equal but different objects
        self.assertEqual(original, copied)
        self.assertEqual(original, deep_copied)
        self.assertIsNot(original, copied)
        self.assertIsNot(original, deep_copied)
        
        # Modifying copy shouldn't affect original
        copied.debug = False
        self.assertTrue(original.debug)
        self.assertFalse(copied.debug)


if __name__ == '__main__':
    unittest.main()

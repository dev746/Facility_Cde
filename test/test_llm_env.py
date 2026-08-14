import importlib
import os
import unittest
from unittest.mock import patch


class TestLLMEnv(unittest.TestCase):
    def test_nemotron_env_overrides_defaults(self):
        with patch.dict(
            os.environ,
            {
                "NEMOTRON_API_KEY": "demo-key",
                "NEMOTRON_BASE_URL": "https://example.test/v1",
                "NEMOTRON_MODEL": "demo/model",
            },
            clear=True,
        ):
            import core.llm as llm_module

            llm_module = importlib.reload(llm_module)
            client = llm_module.get_client()

            self.assertEqual(client.api_key, "demo-key")
            self.assertEqual(str(client.base_url).rstrip('/'), "https://example.test/v1")
            self.assertEqual(llm_module.MODEL, "demo/model")


if __name__ == "__main__":
    unittest.main()

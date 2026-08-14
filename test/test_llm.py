import unittest
import os
from dotenv import load_dotenv
load_dotenv()

class TestLLM(unittest.TestCase):
    def test_llm_connection(self):
        from core.llm import chat
        resp = chat(
            system="You are a helpful assistant. Reply in a warm tone based on parsed information.",
            user="What is a CNC lathe?"
        )
        self.assertIsInstance(resp, str)
        self.assertTrue(len(resp) > 0)

if __name__ == "__main__":
    unittest.main()

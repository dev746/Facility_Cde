import unittest
import sys
from query.intent import parse_intent, extract_asset_name
from core.llm import detect_language

class TestMultilingualResponder(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("where is the hydraulic press"), "english")
        self.assertEqual(detect_language("hydraulic press kahan hai"), "hinglish")
        self.assertEqual(detect_language("एम14 में क्या खराबी है"), "hindi")
        self.assertEqual(detect_language("ಯಂತ್ರದ ಸ್ಥಿತಿ ಏನು"), "kannada")

    def test_asset_name_extraction(self):
        self.assertEqual(extract_asset_name("where is the hydraulic press"), "hydraulic press")
        self.assertEqual(extract_asset_name("M14 ki kya problem hai"), "M14")

    def test_intent_parsing(self):
        r1 = parse_intent("hydraulic press kahan hai")
        self.assertIn(r1["intent"], ["machine", "findings"])
        
        r2 = parse_intent("M14 ki kya problem hai")
        self.assertEqual(r2["intent"], "findings")
        self.assertEqual(r2.get("asset_id"), "M14")

if __name__ == "__main__":
    unittest.main()

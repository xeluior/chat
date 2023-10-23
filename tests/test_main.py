import unittest
import tempfile
import json
import argparse

import chat_cli as chat

class TestMain(unittest.TestCase):
    """Test some of the helper functions used in the main loop"""
    def test_format_prompt(self):
        """Should return a properly formatted prompt"""
        prompt = "%t %T"
        data = {"t": "100", "T": "1000"}
        expected = "100 1000"

        output = chat.format_prompt(prompt, data)
        self.assertEqual(output, expected)
    # end test_format_prompt

    def test_config_prefers_cli(self):
        """Should return the apikey input on the CLI to the one in the config file"""
        expected = "commandline"
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8") as config_file:
            json.dump({ "apikey": "conffile" }, config_file)
            config_file.seek(0)
            args = argparse.Namespace(
                    apikey=expected,
                    config=config_file.name,
                    prompt=None,
                    model=None,
                    resume=False)
            output = chat.load_config(args)
        self.assertEqual(output["apikey"], expected)
    # end test_config_prefers_cli
# end class TestMain

if __name__=="__main__":
    unittest.main()

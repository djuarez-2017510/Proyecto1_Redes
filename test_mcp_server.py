import json
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent
SERVER_FILE = PROJECT_FOLDER / "src" / "mcp_server.py"


class MCPServerTest(unittest.TestCase):
    def send_messages(self, messages):
        input_data = "\n".join(
            json.dumps(message, ensure_ascii=False) for message in messages
        ) + "\n"

        result = subprocess.run(
            [sys.executable, str(SERVER_FILE)],
            input=input_data,
            text=True,
            capture_output=True,
            check=True,
        )

        responses = [
            json.loads(line)
            for line in result.stdout.splitlines()
            if line.strip()
        ]
        return responses

    def base_messages(self):
        return [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "TestClient",
                        "version": "1.0.0",
                    },
                },
            },
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            },
        ]

    def test_initialize(self):
        responses = self.send_messages(self.base_messages())

        self.assertEqual(responses[0]["id"], 1)
        self.assertEqual(
            responses[0]["result"]["protocolVersion"],
            "2025-11-25",
        )

    def test_tools_are_available(self):
        messages = self.base_messages()
        messages.append(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
        )
        responses = self.send_messages(messages)
        tool_names = {
            tool["name"] for tool in responses[1]["result"]["tools"]
        }

        self.assertIn("search_properties", tool_names)
        self.assertIn("schedule_property_visit", tool_names)

    def test_search_properties(self):
        messages = self.base_messages()
        messages.append(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "search_properties",
                    "arguments": {
                        "municipality": "Guatemala",
                        "property_type": "apartment",
                        "bedrooms": 3,
                        "limit": 5,
                    },
                },
            }
        )
        responses = self.send_messages(messages)
        result = responses[1]["result"]["structuredContent"]

        self.assertLessEqual(result["total"], 5)
        for property_data in result["properties"]:
            self.assertEqual(property_data["municipality"], "Guatemala")
            self.assertEqual(property_data["property_type"], "apartment")
            self.assertGreaterEqual(property_data["bedrooms"], 3)
            self.assertEqual(property_data["status"], "available")

    def test_invalid_visit_is_rejected(self):
        messages = self.base_messages()
        messages.append(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "schedule_property_visit",
                    "arguments": {
                        "property_id": "GT-0012",
                        "client_name": "Daniel Juarez",
                        "client_email": "invalid-email",
                        "visit_at": "2026-09-18T15:30:00-06:00",
                    },
                },
            }
        )
        responses = self.send_messages(messages)

        self.assertTrue(responses[1]["result"]["isError"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

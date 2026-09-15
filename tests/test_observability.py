import json
import unittest

from gameweaver.observability import event, request_id


class ObservabilityTests(unittest.TestCase):
    def test_request_id_accepts_safe_value_and_replaces_invalid_value(self):
        self.assertEqual("client-123", request_id("client-123"))
        self.assertNotEqual("bad id\nvalue", request_id("bad id\nvalue"))

    def test_event_is_compact_json(self):
        self.assertEqual({"event": "request", "status": 200}, json.loads(event("request", status=200)))


if __name__ == "__main__":
    unittest.main()

"""Small structured logging helpers."""

import json
import re
from uuid import uuid4


REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


def request_id(value=None):
    return value if value and REQUEST_ID.fullmatch(value) else uuid4().hex


def event(name, **fields):
    return json.dumps({"event": name, **fields}, ensure_ascii=False, separators=(",", ":"))

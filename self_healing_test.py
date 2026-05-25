"""Self-healing API test: tolerates field-name drift via a configured alias map."""
import json
import logging
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
FIXTURE_PATH = BASE_DIR / "expected_shape.json"
BASE_URL = "http://localhost:5001"

ALIASES = {
    "priority":   ["level", "urgency", "rank"],
    "confidence": ["score", "probability", "certainty"],
}

SAMPLE_TASKS = [
    "Fix login bug breaking production",
    "Schedule one on one with manager",
    "Read latest issue of tech magazine",
    "Patch security vulnerability before audit",
    "Plan team offsite for next quarter",
]

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("self_healing_test")


def http_get(url: str):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, json.loads(resp.read())


def http_post_json(url: str, payload: dict):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"_raw": body.decode("utf-8", errors="replace")}


def health_check():
    try:
        status, body = http_get(f"{BASE_URL}/health")
    except Exception as e:
        logger.error("Health check failed — server unreachable: %s", e)
        sys.exit(1)
    if status != 200 or body.get("status") != "ok":
        logger.error("Health check returned %s %s", status, body)
        sys.exit(1)
    logger.info("Health OK")


def resolve_fields(required_fields, live_response):
    """Map each required field to its actual key in the live response.

    Logs SCHEMA_DRIFT WARNING when a field is missing but an alias is found,
    exits non-zero with SCHEMA_BREAK ERROR if neither is present.
    """
    if not isinstance(live_response, dict):
        logger.error("SCHEMA_BREAK ERROR: response body is not a JSON object: %r",
                     live_response)
        sys.exit(1)

    keys = set(live_response.keys())
    mapping = {}
    for field in required_fields:
        if field in keys:
            mapping[field] = field
            continue
        resolved = next((a for a in ALIASES.get(field, []) if a in keys), None)
        if resolved is not None:
            logger.warning(
                "SCHEMA_DRIFT WARNING: field '%s' not found, using '%s' instead",
                field, resolved,
            )
            mapping[field] = resolved
        else:
            logger.error(
                "SCHEMA_BREAK ERROR: field '%s' missing and no known alias found",
                field,
            )
            sys.exit(1)
    return mapping


def main():
    fixture = json.loads(FIXTURE_PATH.read_text())
    required = fixture["required_fields"]
    allowed_priorities = set(fixture["priority_values"])

    health_check()

    logger.info("Warm-up POST /predict to discover response shape")
    status, body = http_post_json(f"{BASE_URL}/predict",
                                  {"task": "Fix critical bug in production"})
    if status != 200:
        logger.error("Warm-up failed with HTTP %s body=%s", status, body)
        sys.exit(1)

    logger.info("Live response keys: %s", sorted(body.keys()))
    mapping = resolve_fields(required, body)
    logger.info("Resolved field mapping: %s", mapping)

    priority_key = mapping["priority"]
    failures = 0
    for task in SAMPLE_TASKS:
        status, body = http_post_json(f"{BASE_URL}/predict", {"task": task})
        priority = body.get(priority_key) if isinstance(body, dict) else None
        ok = status == 200 and priority in allowed_priorities
        marker = "PASS" if ok else "FAIL"
        logger.info("[%s] task=%r -> %s=%r status=%s",
                    marker, task, priority_key, priority, status)
        if not ok:
            failures += 1

    if failures:
        logger.error("%d/%d tasks failed validation", failures, len(SAMPLE_TASKS))
        sys.exit(1)

    logger.info("All %d tasks passed validation", len(SAMPLE_TASKS))
    sys.exit(0)


if __name__ == "__main__":
    main()

# Self-Healing Test — How It Works

**Schema drift** is when an API keeps working but its response shape changes — for example, `/predict` starts returning `level` instead of `priority`. A naïve test that hard-codes `response["priority"]` fails instantly with a `KeyError`, even though the prediction itself is fine.

**Recovery.** `expected_shape.json` defines the contract; `self_healing_test.py` holds an `ALIASES` map (e.g. `priority → [level, urgency, rank]`). After a warm-up call, the script compares live keys to the contract. If a required field is missing it walks the alias list, logs `SCHEMA_DRIFT WARNING`, stores the resolved name, and continues.

**When it gives up.** No alias matches (`SCHEMA_BREAK ERROR`, exit non-zero); the priority value is outside `priority_values`; or the health check fails. Drift is recoverable; semantic breakage isn't.

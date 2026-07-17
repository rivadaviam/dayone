from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import json

PROGRESS_DIR = Path(os.getenv("ONBOARD_PROGRESS_DIR", "/tmp/onboarding-progress"))


def mark_step_done(employee_email: str, step_id: str, note: str = "") -> dict:
    """Track onboarding progress locally.

    This is intentionally file-based for the workshop. In production, replace this
    with DynamoDB writes keyed by employee email / onboarding id.
    """
    PROGRESS_DIR.mkdir(exist_ok=True)
    path = Path(PROGRESS_DIR) / f"{employee_email.replace('@', '_at_')}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"employee_email": employee_email, "steps": []}

    event = {
        "step_id": step_id,
        "note": note,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    data["steps"].append(event)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return event

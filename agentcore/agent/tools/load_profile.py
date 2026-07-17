from pathlib import Path
from typing import Any
import yaml

PROFILES_DIR = Path(__file__).resolve().parents[1] / "profiles"


def load_profile(profile_id: str) -> dict[str, Any]:
    """Load an onboarding profile by id from profiles/<id>.yaml."""
    path = Path(PROFILES_DIR) / f"{profile_id}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in Path(PROFILES_DIR).glob("*.yaml"))
        raise FileNotFoundError(f"Profile '{profile_id}' not found. Available: {available}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

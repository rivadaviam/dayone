from pathlib import Path
from typing import Any
import yaml

PROJECTS_DIR = Path(__file__).resolve().parents[1] / "projects"


def load_project(project_id: str) -> dict[str, Any]:
    """Load a project definition by id from projects/<id>.yaml."""
    path = Path(PROJECTS_DIR) / f"{project_id}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in Path(PROJECTS_DIR).glob("*.yaml"))
        raise FileNotFoundError(f"Project '{project_id}' not found. Available: {available}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

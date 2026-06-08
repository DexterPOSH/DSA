import json
from pathlib import Path

from sysd_buddy.curriculum_data import SYSD_CURRICULUM


def init_curriculum(base_dir: Path) -> dict:
    """Create sysd-curriculum.json if it doesn't exist. Returns status JSON."""
    path = base_dir / "sysd-curriculum.json"
    if path.exists():
        return {"status": "exists", "path": str(path)}
    path.write_text(json.dumps(SYSD_CURRICULUM, indent=2) + "\n")
    return {"status": "created", "path": str(path)}

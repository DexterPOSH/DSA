import json
from datetime import date
from pathlib import Path


def _load_progress(base_dir: Path) -> dict:
    path = base_dir / "sysd-progress.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"current_track": None, "current_category": None, "topics": {}, "category_summary": {}}


def _save_progress(base_dir: Path, data: dict) -> None:
    path = base_dir / "sysd-progress.json"
    path.write_text(json.dumps(data, indent=2) + "\n")


def show_progress(base_dir: Path) -> dict:
    return _load_progress(base_dir)


def update_progress(
    base_dir: Path,
    topic_slug: str,
    status: str | None = None,
    quiz_score: str | None = None,
) -> dict:
    data = _load_progress(base_dir)
    topic = data["topics"].get(topic_slug, {
        "status": "not-started",
        "quiz_score": None,
        "quiz_total": None,
        "completed_at": None,
    })

    if status:
        topic["status"] = status
        if status == "done":
            topic["completed_at"] = date.today().isoformat()

    if quiz_score:
        parts = quiz_score.split("/")
        topic["quiz_score"] = int(parts[0])
        topic["quiz_total"] = int(parts[1])

    data["topics"][topic_slug] = topic
    _save_progress(base_dir, data)
    return {"status": "updated", "topic": topic_slug}

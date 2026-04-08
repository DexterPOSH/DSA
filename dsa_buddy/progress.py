import json
from datetime import date
from pathlib import Path


def _load_progress(base_dir: Path) -> dict:
    path = base_dir / "progress.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"current_category": None, "problems": {}, "category_summary": {}}


def _save_progress(base_dir: Path, data: dict) -> None:
    path = base_dir / "progress.json"
    path.write_text(json.dumps(data, indent=2) + "\n")


def show_progress(base_dir: Path) -> dict:
    return _load_progress(base_dir)


def update_progress(
    base_dir: Path,
    problem_slug: str,
    status: str | None = None,
    quiz_score: str | None = None,
    pytest_result: str | None = None,
) -> dict:
    data = _load_progress(base_dir)
    problem = data["problems"].get(problem_slug, {
        "status": "not-started",
        "quiz_score": None,
        "quiz_total": None,
        "pytest_passed": None,
        "completed_at": None,
    })

    if status:
        problem["status"] = status
        if status == "done":
            problem["completed_at"] = date.today().isoformat()

    if quiz_score:
        parts = quiz_score.split("/")
        problem["quiz_score"] = int(parts[0])
        problem["quiz_total"] = int(parts[1])

    if pytest_result:
        problem["pytest_passed"] = pytest_result == "pass"

    data["problems"][problem_slug] = problem
    _save_progress(base_dir, data)
    return {"status": "updated", "problem": problem_slug}

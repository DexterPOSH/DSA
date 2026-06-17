import json
from pathlib import Path

from dsa_buddy.curriculum_data import CURRICULUM


DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def init_curriculum(base_dir: Path) -> dict:
    """Create curriculum.json if it doesn't exist. Returns status JSON."""
    curriculum_path = base_dir / "curriculum.json"
    if curriculum_path.exists():
        return {"status": "exists", "path": str(curriculum_path)}
    curriculum_path.write_text(json.dumps(CURRICULUM, indent=2) + "\n")
    return {"status": "created", "path": str(curriculum_path)}


def plan_next(base_dir: Path) -> dict:
    """Return the next recommended problem based on progress."""
    from dsa_buddy.progress import show_progress

    curriculum_path = base_dir / "curriculum.json"
    if not curriculum_path.exists():
        return {"error": "No curriculum.json found. Run 'dsa-buddy plan init' first."}

    curriculum = json.loads(curriculum_path.read_text())
    progress = show_progress(base_dir)
    problems_progress = progress.get("problems", {})

    # First pass: find problems needing review (done but score < 60%)
    for category in sorted(curriculum["categories"], key=lambda c: c["order"]):
        for problem in sorted(category["problems"], key=lambda p: DIFFICULTY_ORDER[p["difficulty"]]):
            slug = problem["slug"]
            prog = problems_progress.get(slug, {})
            if prog.get("status") == "done":
                score = prog.get("quiz_score")
                total = prog.get("quiz_total")
                if score is not None and total is not None and total > 0:
                    if (score / total) < 0.6:
                        return {
                            "category": category["slug"],
                            "problem": slug,
                            "difficulty": problem["difficulty"],
                            "reason": f"Review — previous quiz score was {score}/{total} (below 60%)",
                        }

    # Second pass: find first not-done problem
    for category in sorted(curriculum["categories"], key=lambda c: c["order"]):
        for problem in sorted(category["problems"], key=lambda p: DIFFICULTY_ORDER[p["difficulty"]]):
            slug = problem["slug"]
            prog = problems_progress.get(slug, {})
            if prog.get("status") not in ("done",):
                return {
                    "category": category["slug"],
                    "problem": slug,
                    "difficulty": problem["difficulty"],
                    "reason": "Next problem in sequence",
                }

    return {"status": "complete", "reason": "All problems done! You've finished the NeetCode 150."}


def plan_list(base_dir: Path) -> dict:
    """Return full curriculum with progress status."""
    from dsa_buddy.progress import show_progress

    curriculum_path = base_dir / "curriculum.json"
    if not curriculum_path.exists():
        return {"error": "No curriculum.json found. Run 'dsa-buddy plan init' first."}

    curriculum = json.loads(curriculum_path.read_text())
    progress = show_progress(base_dir)
    problems_progress = progress.get("problems", {})

    categories = []
    for category in sorted(curriculum["categories"], key=lambda c: c["order"]):
        done = sum(
            1 for p in category["problems"]
            if problems_progress.get(p["slug"], {}).get("status") == "done"
        )
        categories.append({
            "name": category["name"],
            "slug": category["slug"],
            "done": done,
            "total": len(category["problems"]),
            "problems": [
                {
                    "slug": p["slug"],
                    "difficulty": p["difficulty"],
                    "status": problems_progress.get(p["slug"], {}).get("status", "not-started"),
                }
                for p in category["problems"]
            ],
        })

    return {"categories": categories}

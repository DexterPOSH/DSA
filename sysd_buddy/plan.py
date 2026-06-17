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


def _iter_topics(curriculum: dict):
    """Yield (track, category, topic) in track->category->topic order."""
    for track in sorted(curriculum["tracks"], key=lambda t: t["order"]):
        for category in sorted(track["categories"], key=lambda c: c["order"]):
            for topic in category["topics"]:
                yield track, category, topic


def plan_next(base_dir: Path) -> dict:
    """Return the next recommended topic. Track 2 is gated behind Track 1."""
    from sysd_buddy.progress import show_progress

    path = base_dir / "sysd-curriculum.json"
    if not path.exists():
        return {"error": "No sysd-curriculum.json found. Run 'sysd-buddy plan init' first."}

    curriculum = json.loads(path.read_text())
    topics_progress = show_progress(base_dir).get("topics", {})

    # First pass: review topics that are done but scored below 60%
    for track, category, topic in _iter_topics(curriculum):
        prog = topics_progress.get(topic["slug"], {})
        if prog.get("status") == "done":
            score, total = prog.get("quiz_score"), prog.get("quiz_total")
            if score is not None and total is not None and total > 0 and (score / total) < 0.6:
                return {
                    "track": track["slug"],
                    "category": category["slug"],
                    "topic": topic["slug"],
                    "reason": f"Review — previous quiz score was {score}/{total} (below 60%)",
                }

    # Second pass: first not-done topic in track order (this naturally gates Track 2)
    for track, category, topic in _iter_topics(curriculum):
        if topics_progress.get(topic["slug"], {}).get("status") != "done":
            return {
                "track": track["slug"],
                "category": category["slug"],
                "topic": topic["slug"],
                "reason": "Next topic in sequence",
            }

    return {"status": "complete", "reason": "All topics done! Building Blocks + Design Problems complete."}


def plan_list(base_dir: Path) -> dict:
    """Return the full curriculum annotated with progress."""
    from sysd_buddy.progress import show_progress

    path = base_dir / "sysd-curriculum.json"
    if not path.exists():
        return {"error": "No sysd-curriculum.json found. Run 'sysd-buddy plan init' first."}

    curriculum = json.loads(path.read_text())
    topics_progress = show_progress(base_dir).get("topics", {})

    tracks = []
    for track in sorted(curriculum["tracks"], key=lambda t: t["order"]):
        categories = []
        for category in sorted(track["categories"], key=lambda c: c["order"]):
            done = sum(
                1 for t in category["topics"]
                if topics_progress.get(t["slug"], {}).get("status") == "done"
            )
            categories.append({
                "name": category["name"],
                "slug": category["slug"],
                "done": done,
                "total": len(category["topics"]),
                "topics": [
                    {
                        "name": t["name"],
                        "slug": t["slug"],
                        "status": topics_progress.get(t["slug"], {}).get("status", "not-started"),
                    }
                    for t in category["topics"]
                ],
            })
        tracks.append({"name": track["name"], "slug": track["slug"], "categories": categories})

    return {"tracks": tracks}

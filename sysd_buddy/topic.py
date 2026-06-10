import json
from pathlib import Path


def _find_topic_full(base_dir: Path, topic_slug: str) -> tuple[dict | None, dict | None, dict | None]:
    """Return (track, category, topic) dicts or (None, None, None)."""
    path = base_dir / "sysd-curriculum.json"
    if not path.exists():
        return None, None, None
    curriculum = json.loads(path.read_text())
    for track in curriculum["tracks"]:
        for category in track["categories"]:
            for topic in category["topics"]:
                if topic["slug"] == topic_slug:
                    return track, category, topic
    return None, None, None


def init_topic(base_dir: Path, topic_slug: str) -> dict:
    """Create the topic directory with a concept README template."""
    track, category, topic = _find_topic_full(base_dir, topic_slug)
    if category is None:
        return {"error": f"Topic '{topic_slug}' not found in curriculum."}

    topic_dir = base_dir / "sysd-topics" / category["slug"] / topic_slug
    readme_path = topic_dir / "README.md"
    if readme_path.exists():
        return {"status": "exists", "path": str(topic_dir)}

    topic_dir.mkdir(parents=True, exist_ok=True)
    readme_content = f"""# {topic["name"]}

**Track:** {track["name"]}
**Category:** {category["name"]}

## What It Is

<!-- Agent: one-sentence definition -->

## Real-World Analogy

<!-- Agent: explain with a tangible Hinglish analogy that makes it click -->

## How It Works

<!-- Agent: step-by-step mechanics -->

## Tradeoffs & Variants

<!-- Agent: the decision points an interviewer probes -->

## When To Use It

<!-- Agent: pattern recognition for interviews -->

## Common Interview Gotchas

<!-- Agent: misconceptions and mistakes to avoid -->

## Practice

<!-- Agent: pointer to the conceptual quiz + visual.html -->
"""
    readme_path.write_text(readme_content)
    return {"status": "created", "path": str(topic_dir)}

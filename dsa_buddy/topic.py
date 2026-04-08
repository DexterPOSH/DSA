import json
from pathlib import Path


def _find_problem_full(base_dir: Path, problem_slug: str) -> tuple[dict | None, dict | None]:
    """Return (category, problem) dicts or (None, None)."""
    curriculum_path = base_dir / "curriculum.json"
    if not curriculum_path.exists():
        return None, None
    curriculum = json.loads(curriculum_path.read_text())
    for category in curriculum["categories"]:
        for problem in category["problems"]:
            if problem["slug"] == problem_slug:
                return category, problem
    return None, None


def init_topic(base_dir: Path, problem_slug: str) -> dict:
    """Create topic directory with README template."""
    category, problem = _find_problem_full(base_dir, problem_slug)
    if category is None:
        return {"error": f"Problem '{problem_slug}' not found in curriculum."}

    topic_dir = base_dir / "topics" / category["slug"] / problem_slug
    readme_path = topic_dir / "README.md"

    if readme_path.exists():
        return {"status": "exists", "path": str(topic_dir)}

    topic_dir.mkdir(parents=True, exist_ok=True)

    readme_content = f"""# {problem["name"]}

**Category:** {category["name"]}
**Difficulty:** {problem["difficulty"]}

## Problem Statement

<!-- Agent: fill in the problem description -->

## Real-World Analogy

<!-- Agent: explain this concept using a real-world analogy that makes it click -->

## Approach

<!-- Agent: explain the optimal approach step by step -->

## Complexity

- **Time:** O(?)
- **Space:** O(?)

## Common Pitfalls

<!-- Agent: list common mistakes to watch out for -->

## Visual

<!-- Agent: generate visual.html in this directory using the illustrator subagent -->

## NeetCode Link

<!-- Agent: add the NeetCode.io link for this problem -->
"""
    readme_path.write_text(readme_content)

    return {"status": "created", "path": str(topic_dir)}

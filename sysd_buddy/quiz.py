import json
from pathlib import Path


def _find_topic(base_dir: Path, topic_slug: str) -> tuple[str | None, dict | None]:
    """Return (category_slug, topic_dict) or (None, None)."""
    path = base_dir / "sysd-curriculum.json"
    if not path.exists():
        return None, None
    curriculum = json.loads(path.read_text())
    for track in curriculum["tracks"]:
        for category in track["categories"]:
            for topic in category["topics"]:
                if topic["slug"] == topic_slug:
                    return category["slug"], topic
    return None, None


def scaffold_quiz(base_dir: Path, topic_slug: str) -> dict:
    """Create a conceptual quiz markdown file for a topic (no pytest)."""
    category_slug, topic = _find_topic(base_dir, topic_slug)
    if category_slug is None:
        return {"error": f"Topic '{topic_slug}' not found in curriculum."}

    quiz_dir = base_dir / "sysd-quizzes" / category_slug
    func_name = topic_slug.replace("-", "_")
    quiz_md_path = quiz_dir / f"conceptual_quiz_{func_name}.md"
    if quiz_md_path.exists():
        return {"status": "exists", "path": str(quiz_md_path)}

    quiz_dir.mkdir(parents=True, exist_ok=True)
    quiz_content = f"""# {topic["name"]} — Conceptual Quiz

<!-- Agent (sysd-quiz skill): replace these stub questions with 5-8 real ones.
     Each question MUST include an "Ideal answer" outline of the key points the
     grader looks for, plus a difficulty tag. Grade the user conversationally
     against the Ideal answer, then record the score with:
     `sysd-buddy progress update {topic_slug} --quiz-score N/M` -->

## Q1 (warm-up)
<!-- question text -->

**Ideal answer:** <!-- key points the grader checks for -->

## Q2 (core)
<!-- question text -->

**Ideal answer:** <!-- key points -->

## Q3 (tradeoff)
<!-- question text -->

**Ideal answer:** <!-- key points -->

## Q4 (gotcha)
<!-- question text -->

**Ideal answer:** <!-- key points -->

## Q5 (applied)
<!-- question text -->

**Ideal answer:** <!-- key points -->
"""
    quiz_md_path.write_text(quiz_content)
    return {"status": "created", "path": str(quiz_md_path)}

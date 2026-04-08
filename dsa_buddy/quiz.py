import json
import subprocess
from pathlib import Path


def _find_problem_category(base_dir: Path, problem_slug: str) -> str | None:
    """Look up which category a problem belongs to."""
    curriculum_path = base_dir / "curriculum.json"
    if not curriculum_path.exists():
        return None
    curriculum = json.loads(curriculum_path.read_text())
    for category in curriculum["categories"]:
        for problem in category["problems"]:
            if problem["slug"] == problem_slug:
                return category["slug"]
    return None


def _find_problem_info(base_dir: Path, problem_slug: str) -> dict | None:
    """Look up problem name and difficulty."""
    curriculum_path = base_dir / "curriculum.json"
    if not curriculum_path.exists():
        return None
    curriculum = json.loads(curriculum_path.read_text())
    for category in curriculum["categories"]:
        for problem in category["problems"]:
            if problem["slug"] == problem_slug:
                return problem
    return None


def scaffold_quiz(base_dir: Path, problem_slug: str) -> dict:
    """Create pytest + conceptual quiz files for a problem."""
    category_slug = _find_problem_category(base_dir, problem_slug)
    if category_slug is None:
        return {"error": f"Problem '{problem_slug}' not found in curriculum."}

    problem_info = _find_problem_info(base_dir, problem_slug)
    quiz_dir = base_dir / "quizzes" / category_slug
    func_name = problem_slug.replace("-", "_")
    pytest_path = quiz_dir / f"test_{func_name}.py"
    quiz_md_path = quiz_dir / f"conceptual_quiz_{func_name}.md"

    if pytest_path.exists() or quiz_md_path.exists():
        return {"status": "exists", "path": str(quiz_dir)}

    quiz_dir.mkdir(parents=True, exist_ok=True)

    # Generate pytest stub
    problem_name = problem_info["name"]
    pytest_content = f'''"""
{problem_name} — Coding Challenge

Implement the function below and run the tests to verify.
Difficulty: {problem_info["difficulty"]}

Hint: Think about the most efficient data structure for this problem.
"""


def {func_name}():
    # TODO: Implement this
    pass


def test_basic():
    assert {func_name}() is not None, "Implement {func_name} to solve this problem"


def test_edge_case():
    assert {func_name}() is not None, "Handle edge cases"
'''
    pytest_path.write_text(pytest_content)

    # Generate conceptual quiz stub
    quiz_content = f"""# {problem_name} — Conceptual Quiz

## Q1
What is the brute force time complexity for this problem?
- A) O(1)
- B) O(n)
- C) O(n log n)
- D) O(n²)

**Answer:** D
**Explanation:** The brute force approach checks all pairs.

## Q2
What data structure can optimize this problem?
- A) Array
- B) Hash Map
- C) Linked List
- D) Stack

**Answer:** B
**Explanation:** A hash map allows O(1) lookups to find complements.

## Q3
What is the optimized time complexity?
- A) O(1)
- B) O(n)
- C) O(n log n)
- D) O(n²)

**Answer:** B
**Explanation:** With a hash map, we traverse the array once.

## Q4
What is the space complexity of the optimized solution?
- A) O(1)
- B) O(n)
- C) O(n log n)
- D) O(n²)

**Answer:** B
**Explanation:** The hash map stores up to n elements.

## Q5
Which edge case is most important to consider?
- A) Empty input
- B) Single element
- C) Duplicate values
- D) All of the above

**Answer:** D
**Explanation:** All edge cases should be handled for a robust solution.
"""
    quiz_md_path.write_text(quiz_content)

    return {
        "status": "created",
        "pytest_path": str(pytest_path),
        "quiz_path": str(quiz_md_path),
    }


def check_quiz(base_dir: Path, problem_slug: str) -> dict:
    """Run pytest for a problem and return results."""
    category_slug = _find_problem_category(base_dir, problem_slug)
    if category_slug is None:
        return {"error": f"Problem '{problem_slug}' not found in curriculum."}

    func_name = problem_slug.replace("-", "_")
    pytest_path = base_dir / "quizzes" / category_slug / f"test_{func_name}.py"

    if not pytest_path.exists():
        return {"error": f"No quiz file found at {pytest_path}. Run 'quiz scaffold' first."}

    result = subprocess.run(
        ["python", "-m", "pytest", str(pytest_path), "-v", "--tb=short", "--no-header"],
        capture_output=True,
        text=True,
        cwd=str(base_dir),
    )

    passed = result.returncode == 0
    return {
        "passed": passed,
        "exit_code": result.returncode,
        "output": result.stdout,
        "problem": problem_slug,
    }

# DSA Learning Buddy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI (`dsa-buddy`) with agent-agnostic skills and subagents that generate learning plans, quizzes, and visual explanations for DSA topics aligned with NeetCode.io.

**Architecture:** Two layers — skills & subagents (markdown files, the universal interface) on top of a Python CLI (the data engine). Skills tell any AI agent how to orchestrate study sessions; the CLI manages curriculum, progress, and file scaffolding. All CLI output is JSON.

**Tech Stack:** Python 3.11+, click, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Package config, editable install, CLI entry point |
| `dsa_buddy/__init__.py` | Package marker |
| `dsa_buddy/cli.py` | Click group + subcommand wiring |
| `dsa_buddy/plan.py` | Curriculum loading, adaptive ordering, `plan init/next/list` |
| `dsa_buddy/progress.py` | Progress read/update, category summaries |
| `dsa_buddy/quiz.py` | Quiz scaffolding, pytest runner |
| `dsa_buddy/topic.py` | Topic directory + README template scaffolding |
| `dsa_buddy/curriculum_data.py` | NeetCode roadmap data (all 18 categories + problems) |
| `tests/test_plan.py` | Tests for adaptive ordering logic |
| `tests/test_progress.py` | Tests for progress read/update |
| `tests/test_quiz.py` | Tests for quiz scaffolding and checking |
| `tests/test_topic.py` | Tests for topic directory creation |
| `.claude/skills/dsa-learn/SKILL.md` | Study session orchestrator skill |
| `.claude/skills/dsa-quiz/SKILL.md` | Quiz skill (conversational + pytest) |
| `.claude/skills/dsa-explain/SKILL.md` | Topic explainer skill |
| `.claude/skills/dsa-status/SKILL.md` | Progress summary skill |
| `.claude/agents/illustrator.md` | Illustration generator subagent |
| `.claude/agents/quiz-builder.md` | Quiz content generator subagent |
| `AGENTS.md` | Universal agent instructions |

---

### Task 1: Project Scaffolding & Package Setup

**Files:**
- Create: `pyproject.toml`
- Create: `dsa_buddy/__init__.py`
- Create: `dsa_buddy/cli.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "dsa-buddy"
version = "0.1.0"
description = "DSA learning companion CLI aligned with NeetCode.io"
requires-python = ">=3.11"
dependencies = [
    "click>=8.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
dsa-buddy = "dsa_buddy.cli:cli"
```

- [ ] **Step 2: Create `dsa_buddy/__init__.py`**

```python
"""DSA Learning Buddy — CLI and data engine."""
```

- [ ] **Step 3: Create `dsa_buddy/cli.py` with empty Click groups**

```python
import click


@click.group()
def cli():
    """DSA Learning Buddy — your NeetCode.io study companion."""
    pass


@cli.group()
def plan():
    """Manage your learning plan."""
    pass


@cli.group()
def quiz():
    """Generate and check quizzes."""
    pass


@cli.group()
def progress():
    """Track your learning progress."""
    pass


@cli.group()
def topic():
    """Manage topic content."""
    pass
```

- [ ] **Step 4: Install in editable mode and verify CLI works**

Run: `cd /Users/ddhami/me/dsa/DSA && pip install -e ".[dev]"`

Then: `dsa-buddy --help`

Expected output:
```
Usage: dsa-buddy [OPTIONS] COMMAND [ARGS]...

  DSA Learning Buddy — your NeetCode.io study companion.

Options:
  --help  Show this message and exit.

Commands:
  plan      Manage your learning plan.
  progress  Track your learning progress.
  quiz      Generate and check quizzes.
  topic     Manage topic content.
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml dsa_buddy/__init__.py dsa_buddy/cli.py
git commit -m "feat: scaffold dsa-buddy CLI package with click groups"
```

---

### Task 2: Curriculum Data & `plan init`

**Files:**
- Create: `dsa_buddy/curriculum_data.py`
- Modify: `dsa_buddy/plan.py` (create)
- Modify: `dsa_buddy/cli.py`
- Create: `tests/test_plan.py`

- [ ] **Step 1: Write the failing test for `plan init`**

Create `tests/__init__.py` (empty) and `tests/test_plan.py`:

```python
import json
import os
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_plan_init_creates_curriculum_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "init"])
    assert result.exit_code == 0
    curriculum_path = tmp_path / "curriculum.json"
    assert curriculum_path.exists()
    data = json.loads(curriculum_path.read_text())
    assert data["version"] == 1
    assert len(data["categories"]) == 18
    assert data["categories"][0]["slug"] == "arrays-and-hashing"


def test_plan_init_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "curriculum.json").write_text('{"custom": true}')
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "init"])
    assert result.exit_code == 0
    data = json.loads((tmp_path / "curriculum.json").read_text())
    assert data == {"custom": True}


def test_plan_init_output_is_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "init"])
    output = json.loads(result.output)
    assert output["status"] in ("created", "exists")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_plan.py -v`

Expected: FAIL — `plan init` command not registered.

- [ ] **Step 3: Create `dsa_buddy/curriculum_data.py` with NeetCode roadmap**

```python
"""NeetCode 150 roadmap — all 18 categories with problems."""

CURRICULUM = {
    "version": 1,
    "categories": [
        {
            "name": "Arrays & Hashing",
            "slug": "arrays-and-hashing",
            "order": 1,
            "problems": [
                {"name": "Contains Duplicate", "slug": "contains-duplicate", "difficulty": "easy"},
                {"name": "Valid Anagram", "slug": "valid-anagram", "difficulty": "easy"},
                {"name": "Two Sum", "slug": "two-sum", "difficulty": "easy"},
                {"name": "Group Anagrams", "slug": "group-anagrams", "difficulty": "medium"},
                {"name": "Top K Frequent Elements", "slug": "top-k-frequent-elements", "difficulty": "medium"},
                {"name": "Encode and Decode Strings", "slug": "encode-and-decode-strings", "difficulty": "medium"},
                {"name": "Product of Array Except Self", "slug": "product-of-array-except-self", "difficulty": "medium"},
                {"name": "Valid Sudoku", "slug": "valid-sudoku", "difficulty": "medium"},
                {"name": "Longest Consecutive Sequence", "slug": "longest-consecutive-sequence", "difficulty": "medium"},
            ],
        },
        {
            "name": "Two Pointers",
            "slug": "two-pointers",
            "order": 2,
            "problems": [
                {"name": "Valid Palindrome", "slug": "valid-palindrome", "difficulty": "easy"},
                {"name": "Two Sum II", "slug": "two-sum-ii", "difficulty": "medium"},
                {"name": "3Sum", "slug": "3sum", "difficulty": "medium"},
                {"name": "Container With Most Water", "slug": "container-with-most-water", "difficulty": "medium"},
                {"name": "Trapping Rain Water", "slug": "trapping-rain-water", "difficulty": "hard"},
            ],
        },
        {
            "name": "Sliding Window",
            "slug": "sliding-window",
            "order": 3,
            "problems": [
                {"name": "Best Time to Buy and Sell Stock", "slug": "best-time-to-buy-and-sell-stock", "difficulty": "easy"},
                {"name": "Longest Substring Without Repeating Characters", "slug": "longest-substring-without-repeating-characters", "difficulty": "medium"},
                {"name": "Longest Repeating Character Replacement", "slug": "longest-repeating-character-replacement", "difficulty": "medium"},
                {"name": "Permutation in String", "slug": "permutation-in-string", "difficulty": "medium"},
                {"name": "Minimum Window Substring", "slug": "minimum-window-substring", "difficulty": "hard"},
                {"name": "Sliding Window Maximum", "slug": "sliding-window-maximum", "difficulty": "hard"},
            ],
        },
        {
            "name": "Stack",
            "slug": "stack",
            "order": 4,
            "problems": [
                {"name": "Valid Parentheses", "slug": "valid-parentheses", "difficulty": "easy"},
                {"name": "Min Stack", "slug": "min-stack", "difficulty": "medium"},
                {"name": "Evaluate Reverse Polish Notation", "slug": "evaluate-reverse-polish-notation", "difficulty": "medium"},
                {"name": "Generate Parentheses", "slug": "generate-parentheses", "difficulty": "medium"},
                {"name": "Daily Temperatures", "slug": "daily-temperatures", "difficulty": "medium"},
                {"name": "Car Fleet", "slug": "car-fleet", "difficulty": "medium"},
                {"name": "Largest Rectangle in Histogram", "slug": "largest-rectangle-in-histogram", "difficulty": "hard"},
            ],
        },
        {
            "name": "Binary Search",
            "slug": "binary-search",
            "order": 5,
            "problems": [
                {"name": "Binary Search", "slug": "binary-search", "difficulty": "easy"},
                {"name": "Search a 2D Matrix", "slug": "search-a-2d-matrix", "difficulty": "medium"},
                {"name": "Koko Eating Bananas", "slug": "koko-eating-bananas", "difficulty": "medium"},
                {"name": "Find Minimum in Rotated Sorted Array", "slug": "find-minimum-in-rotated-sorted-array", "difficulty": "medium"},
                {"name": "Search in Rotated Sorted Array", "slug": "search-in-rotated-sorted-array", "difficulty": "medium"},
                {"name": "Time Based Key Value Store", "slug": "time-based-key-value-store", "difficulty": "medium"},
                {"name": "Median of Two Sorted Arrays", "slug": "median-of-two-sorted-arrays", "difficulty": "hard"},
            ],
        },
        {
            "name": "Linked List",
            "slug": "linked-list",
            "order": 6,
            "problems": [
                {"name": "Reverse Linked List", "slug": "reverse-linked-list", "difficulty": "easy"},
                {"name": "Merge Two Sorted Lists", "slug": "merge-two-sorted-lists", "difficulty": "easy"},
                {"name": "Linked List Cycle", "slug": "linked-list-cycle", "difficulty": "easy"},
                {"name": "Reorder List", "slug": "reorder-list", "difficulty": "medium"},
                {"name": "Remove Nth Node From End of List", "slug": "remove-nth-node-from-end-of-list", "difficulty": "medium"},
                {"name": "Copy List With Random Pointer", "slug": "copy-list-with-random-pointer", "difficulty": "medium"},
                {"name": "Add Two Numbers", "slug": "add-two-numbers", "difficulty": "medium"},
                {"name": "Find the Duplicate Number", "slug": "find-the-duplicate-number", "difficulty": "medium"},
                {"name": "LRU Cache", "slug": "lru-cache", "difficulty": "medium"},
                {"name": "Merge K Sorted Lists", "slug": "merge-k-sorted-lists", "difficulty": "hard"},
                {"name": "Reverse Nodes in K Group", "slug": "reverse-nodes-in-k-group", "difficulty": "hard"},
            ],
        },
        {
            "name": "Trees",
            "slug": "trees",
            "order": 7,
            "problems": [
                {"name": "Invert Binary Tree", "slug": "invert-binary-tree", "difficulty": "easy"},
                {"name": "Maximum Depth of Binary Tree", "slug": "maximum-depth-of-binary-tree", "difficulty": "easy"},
                {"name": "Diameter of Binary Tree", "slug": "diameter-of-binary-tree", "difficulty": "easy"},
                {"name": "Balanced Binary Tree", "slug": "balanced-binary-tree", "difficulty": "easy"},
                {"name": "Same Tree", "slug": "same-tree", "difficulty": "easy"},
                {"name": "Subtree of Another Tree", "slug": "subtree-of-another-tree", "difficulty": "easy"},
                {"name": "Lowest Common Ancestor of a BST", "slug": "lowest-common-ancestor-of-a-bst", "difficulty": "medium"},
                {"name": "Binary Tree Level Order Traversal", "slug": "binary-tree-level-order-traversal", "difficulty": "medium"},
                {"name": "Binary Tree Right Side View", "slug": "binary-tree-right-side-view", "difficulty": "medium"},
                {"name": "Count Good Nodes in Binary Tree", "slug": "count-good-nodes-in-binary-tree", "difficulty": "medium"},
                {"name": "Validate Binary Search Tree", "slug": "validate-binary-search-tree", "difficulty": "medium"},
                {"name": "Kth Smallest Element in a BST", "slug": "kth-smallest-element-in-a-bst", "difficulty": "medium"},
                {"name": "Construct Binary Tree from Preorder and Inorder Traversal", "slug": "construct-binary-tree-from-preorder-and-inorder-traversal", "difficulty": "medium"},
                {"name": "Binary Tree Maximum Path Sum", "slug": "binary-tree-maximum-path-sum", "difficulty": "hard"},
                {"name": "Serialize and Deserialize Binary Tree", "slug": "serialize-and-deserialize-binary-tree", "difficulty": "hard"},
            ],
        },
        {
            "name": "Tries",
            "slug": "tries",
            "order": 8,
            "problems": [
                {"name": "Implement Trie", "slug": "implement-trie", "difficulty": "medium"},
                {"name": "Design Add and Search Words Data Structure", "slug": "design-add-and-search-words-data-structure", "difficulty": "medium"},
                {"name": "Word Search II", "slug": "word-search-ii", "difficulty": "hard"},
            ],
        },
        {
            "name": "Heap / Priority Queue",
            "slug": "heap-priority-queue",
            "order": 9,
            "problems": [
                {"name": "Kth Largest Element in a Stream", "slug": "kth-largest-element-in-a-stream", "difficulty": "easy"},
                {"name": "Last Stone Weight", "slug": "last-stone-weight", "difficulty": "easy"},
                {"name": "K Closest Points to Origin", "slug": "k-closest-points-to-origin", "difficulty": "medium"},
                {"name": "Kth Largest Element in an Array", "slug": "kth-largest-element-in-an-array", "difficulty": "medium"},
                {"name": "Task Scheduler", "slug": "task-scheduler", "difficulty": "medium"},
                {"name": "Design Twitter", "slug": "design-twitter", "difficulty": "medium"},
                {"name": "Find Median from Data Stream", "slug": "find-median-from-data-stream", "difficulty": "hard"},
            ],
        },
        {
            "name": "Backtracking",
            "slug": "backtracking",
            "order": 10,
            "problems": [
                {"name": "Subsets", "slug": "subsets", "difficulty": "medium"},
                {"name": "Combination Sum", "slug": "combination-sum", "difficulty": "medium"},
                {"name": "Permutations", "slug": "permutations", "difficulty": "medium"},
                {"name": "Subsets II", "slug": "subsets-ii", "difficulty": "medium"},
                {"name": "Combination Sum II", "slug": "combination-sum-ii", "difficulty": "medium"},
                {"name": "Word Search", "slug": "word-search", "difficulty": "medium"},
                {"name": "Palindrome Partitioning", "slug": "palindrome-partitioning", "difficulty": "medium"},
                {"name": "Letter Combinations of a Phone Number", "slug": "letter-combinations-of-a-phone-number", "difficulty": "medium"},
                {"name": "N Queens", "slug": "n-queens", "difficulty": "hard"},
            ],
        },
        {
            "name": "Graphs",
            "slug": "graphs",
            "order": 11,
            "problems": [
                {"name": "Number of Islands", "slug": "number-of-islands", "difficulty": "medium"},
                {"name": "Clone Graph", "slug": "clone-graph", "difficulty": "medium"},
                {"name": "Max Area of Island", "slug": "max-area-of-island", "difficulty": "medium"},
                {"name": "Pacific Atlantic Water Flow", "slug": "pacific-atlantic-water-flow", "difficulty": "medium"},
                {"name": "Surrounded Regions", "slug": "surrounded-regions", "difficulty": "medium"},
                {"name": "Rotting Oranges", "slug": "rotting-oranges", "difficulty": "medium"},
                {"name": "Walls and Gates", "slug": "walls-and-gates", "difficulty": "medium"},
                {"name": "Course Schedule", "slug": "course-schedule", "difficulty": "medium"},
                {"name": "Course Schedule II", "slug": "course-schedule-ii", "difficulty": "medium"},
                {"name": "Redundant Connection", "slug": "redundant-connection", "difficulty": "medium"},
                {"name": "Number of Connected Components in an Undirected Graph", "slug": "number-of-connected-components-in-an-undirected-graph", "difficulty": "medium"},
                {"name": "Graph Valid Tree", "slug": "graph-valid-tree", "difficulty": "medium"},
                {"name": "Word Ladder", "slug": "word-ladder", "difficulty": "hard"},
            ],
        },
        {
            "name": "Advanced Graphs",
            "slug": "advanced-graphs",
            "order": 12,
            "problems": [
                {"name": "Reconstruct Itinerary", "slug": "reconstruct-itinerary", "difficulty": "hard"},
                {"name": "Min Cost to Connect All Points", "slug": "min-cost-to-connect-all-points", "difficulty": "medium"},
                {"name": "Network Delay Time", "slug": "network-delay-time", "difficulty": "medium"},
                {"name": "Swim in Rising Water", "slug": "swim-in-rising-water", "difficulty": "hard"},
                {"name": "Alien Dictionary", "slug": "alien-dictionary", "difficulty": "hard"},
                {"name": "Cheapest Flights Within K Stops", "slug": "cheapest-flights-within-k-stops", "difficulty": "medium"},
            ],
        },
        {
            "name": "1-D Dynamic Programming",
            "slug": "1d-dynamic-programming",
            "order": 13,
            "problems": [
                {"name": "Climbing Stairs", "slug": "climbing-stairs", "difficulty": "easy"},
                {"name": "Min Cost Climbing Stairs", "slug": "min-cost-climbing-stairs", "difficulty": "easy"},
                {"name": "House Robber", "slug": "house-robber", "difficulty": "medium"},
                {"name": "House Robber II", "slug": "house-robber-ii", "difficulty": "medium"},
                {"name": "Longest Palindromic Substring", "slug": "longest-palindromic-substring", "difficulty": "medium"},
                {"name": "Palindromic Substrings", "slug": "palindromic-substrings", "difficulty": "medium"},
                {"name": "Decode Ways", "slug": "decode-ways", "difficulty": "medium"},
                {"name": "Coin Change", "slug": "coin-change", "difficulty": "medium"},
                {"name": "Maximum Product Subarray", "slug": "maximum-product-subarray", "difficulty": "medium"},
                {"name": "Word Break", "slug": "word-break", "difficulty": "medium"},
                {"name": "Longest Increasing Subsequence", "slug": "longest-increasing-subsequence", "difficulty": "medium"},
                {"name": "Partition Equal Subset Sum", "slug": "partition-equal-subset-sum", "difficulty": "medium"},
            ],
        },
        {
            "name": "2-D Dynamic Programming",
            "slug": "2d-dynamic-programming",
            "order": 14,
            "problems": [
                {"name": "Unique Paths", "slug": "unique-paths", "difficulty": "medium"},
                {"name": "Longest Common Subsequence", "slug": "longest-common-subsequence", "difficulty": "medium"},
                {"name": "Best Time to Buy and Sell Stock with Cooldown", "slug": "best-time-to-buy-and-sell-stock-with-cooldown", "difficulty": "medium"},
                {"name": "Coin Change II", "slug": "coin-change-ii", "difficulty": "medium"},
                {"name": "Target Sum", "slug": "target-sum", "difficulty": "medium"},
                {"name": "Interleaving String", "slug": "interleaving-string", "difficulty": "medium"},
                {"name": "Longest Increasing Path in a Matrix", "slug": "longest-increasing-path-in-a-matrix", "difficulty": "hard"},
                {"name": "Distinct Subsequences", "slug": "distinct-subsequences", "difficulty": "hard"},
                {"name": "Edit Distance", "slug": "edit-distance", "difficulty": "medium"},
                {"name": "Burst Balloons", "slug": "burst-balloons", "difficulty": "hard"},
                {"name": "Regular Expression Matching", "slug": "regular-expression-matching", "difficulty": "hard"},
            ],
        },
        {
            "name": "Greedy",
            "slug": "greedy",
            "order": 15,
            "problems": [
                {"name": "Maximum Subarray", "slug": "maximum-subarray", "difficulty": "medium"},
                {"name": "Jump Game", "slug": "jump-game", "difficulty": "medium"},
                {"name": "Jump Game II", "slug": "jump-game-ii", "difficulty": "medium"},
                {"name": "Gas Station", "slug": "gas-station", "difficulty": "medium"},
                {"name": "Hand of Straights", "slug": "hand-of-straights", "difficulty": "medium"},
                {"name": "Merge Triplets to Form Target Triplet", "slug": "merge-triplets-to-form-target-triplet", "difficulty": "medium"},
                {"name": "Partition Labels", "slug": "partition-labels", "difficulty": "medium"},
                {"name": "Valid Parenthesis String", "slug": "valid-parenthesis-string", "difficulty": "medium"},
            ],
        },
        {
            "name": "Intervals",
            "slug": "intervals",
            "order": 16,
            "problems": [
                {"name": "Insert Interval", "slug": "insert-interval", "difficulty": "medium"},
                {"name": "Merge Intervals", "slug": "merge-intervals", "difficulty": "medium"},
                {"name": "Non Overlapping Intervals", "slug": "non-overlapping-intervals", "difficulty": "medium"},
                {"name": "Meeting Rooms", "slug": "meeting-rooms", "difficulty": "easy"},
                {"name": "Meeting Rooms II", "slug": "meeting-rooms-ii", "difficulty": "medium"},
                {"name": "Minimum Interval to Include Each Query", "slug": "minimum-interval-to-include-each-query", "difficulty": "hard"},
            ],
        },
        {
            "name": "Math & Geometry",
            "slug": "math-and-geometry",
            "order": 17,
            "problems": [
                {"name": "Rotate Image", "slug": "rotate-image", "difficulty": "medium"},
                {"name": "Spiral Matrix", "slug": "spiral-matrix", "difficulty": "medium"},
                {"name": "Set Matrix Zeroes", "slug": "set-matrix-zeroes", "difficulty": "medium"},
                {"name": "Happy Number", "slug": "happy-number", "difficulty": "easy"},
                {"name": "Plus One", "slug": "plus-one", "difficulty": "easy"},
                {"name": "Pow(x, n)", "slug": "powx-n", "difficulty": "medium"},
                {"name": "Multiply Strings", "slug": "multiply-strings", "difficulty": "medium"},
                {"name": "Detect Squares", "slug": "detect-squares", "difficulty": "medium"},
            ],
        },
        {
            "name": "Bit Manipulation",
            "slug": "bit-manipulation",
            "order": 18,
            "problems": [
                {"name": "Single Number", "slug": "single-number", "difficulty": "easy"},
                {"name": "Number of 1 Bits", "slug": "number-of-1-bits", "difficulty": "easy"},
                {"name": "Counting Bits", "slug": "counting-bits", "difficulty": "easy"},
                {"name": "Reverse Bits", "slug": "reverse-bits", "difficulty": "easy"},
                {"name": "Missing Number", "slug": "missing-number", "difficulty": "easy"},
                {"name": "Sum of Two Integers", "slug": "sum-of-two-integers", "difficulty": "medium"},
                {"name": "Reverse Integer", "slug": "reverse-integer", "difficulty": "medium"},
            ],
        },
    ],
}
```

- [ ] **Step 4: Create `dsa_buddy/plan.py` with `init` command logic**

```python
import json
from pathlib import Path

from dsa_buddy.curriculum_data import CURRICULUM


def init_curriculum(base_dir: Path) -> dict:
    """Create curriculum.json if it doesn't exist. Returns status JSON."""
    curriculum_path = base_dir / "curriculum.json"
    if curriculum_path.exists():
        return {"status": "exists", "path": str(curriculum_path)}
    curriculum_path.write_text(json.dumps(CURRICULUM, indent=2) + "\n")
    return {"status": "created", "path": str(curriculum_path)}
```

- [ ] **Step 5: Wire `plan init` into `cli.py`**

Add to `dsa_buddy/cli.py`:

```python
import json
from pathlib import Path

import click


@click.group()
def cli():
    """DSA Learning Buddy — your NeetCode.io study companion."""
    pass


@cli.group()
def plan():
    """Manage your learning plan."""
    pass


@cli.group()
def quiz():
    """Generate and check quizzes."""
    pass


@cli.group()
def progress():
    """Track your learning progress."""
    pass


@cli.group()
def topic():
    """Manage topic content."""
    pass


@plan.command("init")
def plan_init():
    """Seed curriculum.json with the NeetCode 150 roadmap."""
    from dsa_buddy.plan import init_curriculum

    result = init_curriculum(Path.cwd())
    click.echo(json.dumps(result))
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_plan.py -v`

Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add dsa_buddy/ tests/ pyproject.toml
git commit -m "feat: add curriculum data and plan init command"
```

---

### Task 3: Progress Module — `progress show` & `progress update`

**Files:**
- Create: `dsa_buddy/progress.py`
- Modify: `dsa_buddy/cli.py`
- Create: `tests/test_progress.py`

- [ ] **Step 1: Write failing tests for progress**

Create `tests/test_progress.py`:

```python
import json
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_progress_show_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["progress", "show"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["current_category"] is None
    assert data["problems"] == {}
    assert data["category_summary"] == {}


def test_progress_show_with_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    progress_data = {
        "current_category": "arrays-and-hashing",
        "problems": {
            "two-sum": {
                "status": "done",
                "quiz_score": 4,
                "quiz_total": 5,
                "pytest_passed": True,
                "completed_at": "2026-04-08",
            }
        },
        "category_summary": {"arrays-and-hashing": {"done": 1, "total": 9}},
    }
    (tmp_path / "progress.json").write_text(json.dumps(progress_data))
    runner = CliRunner()
    result = runner.invoke(cli, ["progress", "show"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["current_category"] == "arrays-and-hashing"
    assert data["problems"]["two-sum"]["status"] == "done"


def test_progress_update_new_problem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["progress", "update", "two-sum", "--status", "done", "--quiz-score", "4/5", "--pytest", "pass"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "updated"
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["problems"]["two-sum"]["status"] == "done"
    assert progress["problems"]["two-sum"]["quiz_score"] == 4
    assert progress["problems"]["two-sum"]["quiz_total"] == 5
    assert progress["problems"]["two-sum"]["pytest_passed"] is True


def test_progress_update_partial(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    # First update — just status
    runner.invoke(cli, ["progress", "update", "two-sum", "--status", "in-progress"])
    # Second update — add quiz score
    result = runner.invoke(cli, ["progress", "update", "two-sum", "--quiz-score", "3/5"])
    assert result.exit_code == 0
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["problems"]["two-sum"]["status"] == "in-progress"
    assert progress["problems"]["two-sum"]["quiz_score"] == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_progress.py -v`

Expected: FAIL — commands not registered.

- [ ] **Step 3: Create `dsa_buddy/progress.py`**

```python
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
```

- [ ] **Step 4: Wire `progress show` and `progress update` into `cli.py`**

Add to `dsa_buddy/cli.py` after the existing groups:

```python
@progress.command("show")
def progress_show():
    """Show current learning progress."""
    from dsa_buddy.progress import show_progress

    result = show_progress(Path.cwd())
    click.echo(json.dumps(result, indent=2))


@progress.command("update")
@click.argument("problem")
@click.option("--status", type=click.Choice(["not-started", "in-progress", "done"]))
@click.option("--quiz-score", help="Score as N/M (e.g. 4/5)")
@click.option("--pytest", "pytest_result", type=click.Choice(["pass", "fail"]))
def progress_update(problem, status, quiz_score, pytest_result):
    """Update progress for a problem."""
    from dsa_buddy.progress import update_progress

    result = update_progress(Path.cwd(), problem, status, quiz_score, pytest_result)
    click.echo(json.dumps(result))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_progress.py -v`

Expected: 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add dsa_buddy/progress.py dsa_buddy/cli.py tests/test_progress.py
git commit -m "feat: add progress show and update commands"
```

---

### Task 4: Adaptive Ordering — `plan next` & `plan list`

**Files:**
- Modify: `dsa_buddy/plan.py`
- Modify: `dsa_buddy/cli.py`
- Modify: `tests/test_plan.py`

- [ ] **Step 1: Write failing tests for `plan next` and `plan list`**

Append to `tests/test_plan.py`:

```python
def test_plan_next_first_problem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["plan", "next"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["category"] == "arrays-and-hashing"
    assert data["problem"] == "contains-duplicate"
    assert data["difficulty"] == "easy"
    assert "reason" in data


def test_plan_next_skips_done(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    # Mark first problem done with high score
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["problem"] == "valid-anagram"


def test_plan_next_resurfaces_low_score(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    # Mark first problem done with low score (below 60%)
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "2/5"])
    # Mark second problem done with high score
    runner.invoke(cli, ["progress", "update", "valid-anagram", "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    # Should resurface contains-duplicate for review, not skip to two-sum
    assert data["problem"] == "contains-duplicate"
    assert "review" in data["reason"].lower()


def test_plan_next_advances_category(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    # Mark all arrays-and-hashing problems done with high scores
    slugs = [
        "contains-duplicate", "valid-anagram", "two-sum", "group-anagrams",
        "top-k-frequent-elements", "encode-and-decode-strings",
        "product-of-array-except-self", "valid-sudoku", "longest-consecutive-sequence",
    ]
    for slug in slugs:
        runner.invoke(cli, ["progress", "update", slug, "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["category"] == "two-pointers"


def test_plan_list_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data["categories"]) == 18
    cat = data["categories"][0]
    assert cat["slug"] == "arrays-and-hashing"
    assert cat["done"] == 1
    assert cat["total"] == 9
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_plan.py -v`

Expected: New tests FAIL — `plan next` and `plan list` not implemented.

- [ ] **Step 3: Implement `plan_next` and `plan_list` in `dsa_buddy/plan.py`**

Add to `dsa_buddy/plan.py`:

```python
from dsa_buddy.progress import show_progress

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def plan_next(base_dir: Path) -> dict:
    """Return the next recommended problem based on progress."""
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
```

- [ ] **Step 4: Wire `plan next` and `plan list` into `cli.py`**

Add to `dsa_buddy/cli.py` after `plan_init`:

```python
@plan.command("next")
def plan_next_cmd():
    """Get the next recommended problem to study."""
    from dsa_buddy.plan import plan_next

    result = plan_next(Path.cwd())
    click.echo(json.dumps(result, indent=2))


@plan.command("list")
def plan_list_cmd():
    """Show full curriculum with progress."""
    from dsa_buddy.plan import plan_list

    result = plan_list(Path.cwd())
    click.echo(json.dumps(result, indent=2))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_plan.py -v`

Expected: 8 tests PASS (3 from Task 2 + 5 new).

- [ ] **Step 6: Commit**

```bash
git add dsa_buddy/plan.py dsa_buddy/cli.py tests/test_plan.py
git commit -m "feat: add plan next with adaptive ordering and plan list"
```

---

### Task 5: Quiz Module — `quiz scaffold` & `quiz check`

**Files:**
- Create: `dsa_buddy/quiz.py`
- Modify: `dsa_buddy/cli.py`
- Create: `tests/test_quiz.py`

- [ ] **Step 1: Write failing tests for quiz commands**

Create `tests/test_quiz.py`:

```python
import json
from pathlib import Path
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_quiz_scaffold_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Need curriculum for category lookup
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "created"
    # Check pytest file exists
    pytest_path = tmp_path / "quizzes" / "arrays-and-hashing" / "test_two_sum.py"
    assert pytest_path.exists()
    content = pytest_path.read_text()
    assert "def two_sum(" in content
    assert "def test_" in content
    # Check conceptual quiz exists
    quiz_path = tmp_path / "quizzes" / "arrays-and-hashing" / "conceptual_quiz_two_sum.md"
    assert quiz_path.exists()


def test_quiz_scaffold_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
    # Modify file
    pytest_path = tmp_path / "quizzes" / "arrays-and-hashing" / "test_two_sum.py"
    pytest_path.write_text("# my custom code")
    result = runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
    data = json.loads(result.output)
    assert data["status"] == "exists"
    assert pytest_path.read_text() == "# my custom code"


def test_quiz_scaffold_unknown_problem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["quiz", "scaffold", "nonexistent"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "error" in data


def test_quiz_check_runs_pytest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
    # Without implementing, tests should fail
    result = runner.invoke(cli, ["quiz", "check", "two-sum"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["passed"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_quiz.py -v`

Expected: FAIL — commands not registered.

- [ ] **Step 3: Create `dsa_buddy/quiz.py`**

```python
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
```

- [ ] **Step 4: Wire `quiz scaffold` and `quiz check` into `cli.py`**

Add to `dsa_buddy/cli.py`:

```python
@quiz.command("scaffold")
@click.argument("problem")
def quiz_scaffold(problem):
    """Create pytest + conceptual quiz files for a problem."""
    from dsa_buddy.quiz import scaffold_quiz

    result = scaffold_quiz(Path.cwd(), problem)
    click.echo(json.dumps(result))


@quiz.command("check")
@click.argument("problem")
def quiz_check(problem):
    """Run pytest for a problem and return results."""
    from dsa_buddy.quiz import check_quiz

    result = check_quiz(Path.cwd(), problem)
    click.echo(json.dumps(result))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_quiz.py -v`

Expected: 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add dsa_buddy/quiz.py dsa_buddy/cli.py tests/test_quiz.py
git commit -m "feat: add quiz scaffold and check commands"
```

---

### Task 6: Topic Module — `topic init`

**Files:**
- Create: `dsa_buddy/topic.py`
- Modify: `dsa_buddy/cli.py`
- Create: `tests/test_topic.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_topic.py`:

```python
import json
from pathlib import Path
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_topic_init_creates_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["topic", "init", "two-sum"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "created"
    topic_dir = tmp_path / "topics" / "arrays-and-hashing" / "two-sum"
    assert topic_dir.exists()
    readme = topic_dir / "README.md"
    assert readme.exists()
    content = readme.read_text()
    assert "Two Sum" in content
    assert "Real-World Analogy" in content


def test_topic_init_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["topic", "init", "two-sum"])
    readme = tmp_path / "topics" / "arrays-and-hashing" / "two-sum" / "README.md"
    readme.write_text("# Custom content")
    result = runner.invoke(cli, ["topic", "init", "two-sum"])
    data = json.loads(result.output)
    assert data["status"] == "exists"
    assert readme.read_text() == "# Custom content"


def test_topic_init_unknown_problem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["topic", "init", "nonexistent"])
    data = json.loads(result.output)
    assert "error" in data
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_topic.py -v`

Expected: FAIL.

- [ ] **Step 3: Create `dsa_buddy/topic.py`**

```python
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
```

- [ ] **Step 4: Wire `topic init` into `cli.py`**

Add to `dsa_buddy/cli.py`:

```python
@topic.command("init")
@click.argument("problem")
def topic_init(problem):
    """Create topic directory with README template."""
    from dsa_buddy.topic import init_topic

    result = init_topic(Path.cwd(), problem)
    click.echo(json.dumps(result))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_topic.py -v`

Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add dsa_buddy/topic.py dsa_buddy/cli.py tests/test_topic.py
git commit -m "feat: add topic init command with README template"
```

---

### Task 7: Skills — dsa-learn, dsa-quiz, dsa-explain, dsa-status

**Files:**
- Create: `.claude/skills/dsa-learn/SKILL.md`
- Create: `.claude/skills/dsa-quiz/SKILL.md`
- Create: `.claude/skills/dsa-explain/SKILL.md`
- Create: `.claude/skills/dsa-status/SKILL.md`

- [ ] **Step 1: Create `.claude/skills/dsa-learn/SKILL.md`**

```markdown
---
name: dsa-learn
description: Start a DSA study session. Reads your progress, recommends what to study next, and coordinates quiz/explain/coding flows. Invoke with "let's study DSA", "study session", or "dsa learn".
---

You are a DSA study buddy helping the user work through NeetCode 150 problems in Python. The user is rusty on DSA — they know the concepts but need them refreshed with clear explanations and real-world analogies.

## Session Flow

1. Run `dsa-buddy progress show` to get current state.
2. If the output shows `current_category: null` and empty problems, this is the first session:
   - Run `dsa-buddy plan init` to seed the curriculum.
   - Welcome the user and explain how the system works.
3. Run `dsa-buddy plan next` to get the recommended problem.
4. Present a brief status summary:
   - Current category and progress (e.g., "Arrays & Hashing: 3/9 done")
   - The recommended next problem and why
5. Offer three choices:
   - **Explain** — "Want me to explain this topic first?" → invoke dsa-explain skill
   - **Quiz** — "Ready for a quiz?" → invoke dsa-quiz skill
   - **Code** — "Want to jump into coding?" → invoke dsa-quiz skill in pytest mode
6. After each activity, run `dsa-buddy progress update <problem> --status <status>` with appropriate flags.

## Tone

- Encouraging but not patronizing
- Use real-world analogies to make concepts click
- Keep explanations concise — the user knows programming, just rusty on DSA
- Celebrate progress: "Nice, that's 5/9 in Arrays & Hashing!"
```

- [ ] **Step 2: Create `.claude/skills/dsa-quiz/SKILL.md`**

```markdown
---
name: dsa-quiz
description: Take a DSA quiz — either conversational (agent asks questions) or pytest (coding challenge). Invoke with "quiz me", "dsa quiz", or "test me on <topic>".
---

You are quizzing the user on DSA concepts. Two modes available.

## Mode Selection

If the user says "quiz me" or "conceptual quiz" → conversational mode.
If the user says "code challenge", "coding quiz", or "pytest" → pytest mode.
If unclear, ask: "Conceptual quiz (I ask questions) or coding challenge (you implement a solution)?"

## Conversational Mode

1. Get the current topic from `dsa-buddy plan next` (or use the topic the user specified).
2. Check if `quizzes/<category>/conceptual_quiz_<problem>.md` exists by looking in the quizzes directory.
3. If not, spawn the `quiz-builder` subagent to create it.
4. Read the quiz file. Ask questions ONE AT A TIME.
5. Do NOT reveal the answer before the user responds.
6. After each answer:
   - If correct: "Correct!" + brief reinforcement.
   - If wrong: "Not quite — the answer is X because..." + clear explanation.
7. After all questions, report the score (e.g., "4/5 — solid!").
8. Run: `dsa-buddy progress update <problem> --quiz-score <score>/<total>`

## Pytest Mode

1. Get the current topic from `dsa-buddy plan next` (or use the topic the user specified).
2. Run `dsa-buddy quiz scaffold <problem>` to create the test file if needed.
3. Tell the user the file path and what to implement.
4. When the user says they're ready, run `dsa-buddy quiz check <problem>`.
5. If tests pass: "All tests pass!" → `dsa-buddy progress update <problem> --pytest pass`
6. If tests fail: show the failures, offer hints, let them try again.
```

- [ ] **Step 3: Create `.claude/skills/dsa-explain/SKILL.md`**

```markdown
---
name: dsa-explain
description: Explain a DSA topic with real-world analogies and visual illustrations. Invoke with "explain <topic>", "teach me about <topic>", or "what is <topic>".
---

You are explaining a DSA concept to someone who is rusty — they've seen this before but need it to click again. Use real-world analogies and clear step-by-step breakdowns.

## Flow

1. Get the topic from the user's request or from `dsa-buddy plan next`.
2. Run `dsa-buddy topic init <problem>` to create the topic directory if needed.
3. Read `topics/<category>/<problem>/README.md` if it already has content.
4. Generate or present the explanation covering:
   - **What it is** — one sentence definition
   - **Real-world analogy** — make it tangible (e.g., "A hash map is like a coat check — you hand over your coat and get a numbered ticket...")
   - **How it works** — step-by-step walkthrough
   - **Time & space complexity** — with intuition for why
   - **Common pitfalls** — mistakes to watch out for
   - **When to use it** — pattern recognition for interviews
5. Spawn the `illustrator` subagent to generate a visual explanation:
   - For the specific problem: save as `topics/<category>/<problem>/visual.html`
   - For the broader concept: save in `illustrations/<category>/`
6. Update the topic README with the generated content.
7. Tell the user about the visual file they can open in their browser.

## Style

- Lead with the analogy — make it memorable
- Use concrete examples, not abstract descriptions
- Keep code examples short (5-10 lines max)
- Reference NeetCode.io for the full problem
```

- [ ] **Step 4: Create `.claude/skills/dsa-status/SKILL.md`**

```markdown
---
name: dsa-status
description: Show DSA learning progress — what you've done, what's next, weak areas. Invoke with "dsa status", "where am I", "show progress", or "how am I doing".
---

You are showing the user their DSA learning progress.

## Flow

1. Run `dsa-buddy progress show` to get the full progress JSON.
2. Run `dsa-buddy plan list` to get the curriculum with statuses.
3. Present a clear summary:
   - **Overall:** X/150 problems completed
   - **Current category:** name + progress (e.g., "Arrays & Hashing: 5/9")
   - **Categories breakdown:** table or list showing done/total per category
   - **Weak areas:** any problems with quiz scores below 60% — suggest reviewing
   - **Next up:** the recommended next problem from `dsa-buddy plan next`
4. If no progress exists yet, say: "You haven't started yet! Say 'let's study DSA' to begin."

## Tone

- Factual and encouraging
- Highlight progress, not gaps
- If they've been consistent: "You're on a roll!"
- If returning after a break: "Welcome back! Let's pick up where you left off."
```

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/
git commit -m "feat: add dsa-learn, dsa-quiz, dsa-explain, dsa-status skills"
```

---

### Task 8: Subagents — illustrator & quiz-builder

**Files:**
- Create: `.claude/agents/illustrator.md`
- Create: `.claude/agents/quiz-builder.md`

- [ ] **Step 1: Create `.claude/agents/illustrator.md`**

```markdown
---
name: illustrator
description: Generates HTML/SVG visual explanations for DSA topics with real-world analogies and step-by-step breakdowns.
---

You generate visual explanations for DSA topics. Your output is self-contained HTML or SVG files that open in any browser.

## Output Conventions

### HTML files (interactive walkthroughs)

- Self-contained: all CSS and JS inline, no external dependencies.
- Dark theme with good contrast (background: #1a1a2e, text: #e0e0e0, accents: #3b82f6).
- Structure:
  1. **Title** — what this visualization shows
  2. **Real-world analogy box** — highlighted callout with the analogy
  3. **Step-by-step walkthrough** — numbered steps with visual state at each step
  4. **Key takeaway** — one sentence summary
- Use CSS animations or simple JS to show state transitions (e.g., elements moving, colors changing).
- Keep it simple — no heavy frameworks, no canvas unless necessary.

### SVG files (static diagrams)

- Clean, readable diagrams for data structures.
- Use consistent colors: nodes (#3b82f6), pointers (#f59e0b), highlights (#10b981).
- Include labels and annotations.
- Suitable for embedding in Markdown.

## Where to Save

- Problem-specific visuals: `topics/<category>/<problem>/visual.html`
- Category-level concept visuals: `illustrations/<category>/<descriptive-name>.html`
- Static diagrams: `illustrations/<category>/<descriptive-name>.svg`

## Examples of Good Analogies

- **Hash Map** → coat check (hand in item, get a ticket number)
- **Stack** → stack of plates (last one placed is first one removed)
- **Queue** → waiting in line at a coffee shop
- **Binary Search** → guessing a number ("higher/lower" game)
- **Linked List** → treasure hunt (each clue points to the next location)
- **Tree** → family tree or org chart
- **Graph** → road map between cities
- **Dynamic Programming** → breaking a trip into legs, optimizing each one
```

- [ ] **Step 2: Create `.claude/agents/quiz-builder.md`**

```markdown
---
name: quiz-builder
description: Generates conceptual quiz markdown and pytest challenge files for DSA problems.
---

You generate quiz content for DSA problems. You create two types of files.

## Conceptual Quiz (Markdown)

Save to: `quizzes/<category>/conceptual_quiz_<problem_slug>.md`

Structure:
```
# <Problem Name> — Conceptual Quiz

## Q1
<Question about time/space complexity>
- A) ...
- B) ...
- C) ...
- D) ...

**Answer:** <letter>
**Explanation:** <1-2 sentences>
```

### Rules

- Exactly 5 questions per quiz.
- Cover: time complexity, space complexity, data structure choice, edge cases, and one "which approach" question.
- All 4 options must be plausible — no obviously wrong distractors.
- Explanations should teach, not just state the answer.

## Pytest Challenge

Save to: `quizzes/<category>/test_<problem_slug>.py`

Structure:
```python
"""
<Problem Name> — Coding Challenge

<Problem description in 2-3 sentences>

Hint: <One helpful hint without giving away the solution>
"""

def <function_name>(<params>) -> <return_type>:
    # TODO: Implement this
    pass

def test_basic():
    assert <function_name>(<basic_input>) == <expected>

def test_edge_case():
    assert <function_name>(<edge_input>) == <expected>

def test_large():
    assert <function_name>(<larger_input>) == <expected>
```

### Rules

- Function name = problem slug with hyphens replaced by underscores.
- Include type hints on the function signature.
- At least 3 test cases: basic, edge case, and a larger input.
- Hints should point toward the right data structure or technique without revealing the algorithm.
- The function stub has `pass` — the user implements it.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/
git commit -m "feat: add illustrator and quiz-builder subagents"
```

---

### Task 9: AGENTS.md — Universal Agent Instructions

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Create `AGENTS.md`**

```markdown
# AGENTS.md — DSA Learning Buddy

This file provides instructions for any AI coding agent working in this repository.

## What This Repo Is

A personal DSA (Data Structures & Algorithms) learning companion built around the NeetCode 150 roadmap. The user is refreshing their DSA knowledge using Python.

## Available CLI Commands

Install: `pip install -e ".[dev]"` from repo root.

| Command | Description | Output |
|---------|-------------|--------|
| `dsa-buddy plan init` | Seed curriculum.json with NeetCode 150 | JSON: {status} |
| `dsa-buddy plan next` | Get next recommended problem | JSON: {category, problem, difficulty, reason} |
| `dsa-buddy plan list` | Show full curriculum with progress | JSON: {categories: [...]} |
| `dsa-buddy quiz scaffold <problem>` | Create pytest + quiz files | JSON: {status, paths} |
| `dsa-buddy quiz check <problem>` | Run pytest for a problem | JSON: {passed, output} |
| `dsa-buddy progress show` | Show current progress | JSON: {current_category, problems, category_summary} |
| `dsa-buddy progress update <problem>` | Update progress | JSON: {status} |
| `dsa-buddy topic init <problem>` | Create topic directory | JSON: {status, path} |

All commands output JSON for easy parsing.

## Available Skills

Skills in `.claude/skills/` describe agent behaviors:

- **dsa-learn** — Study session orchestrator. Start here.
- **dsa-quiz** — Conversational quizzes + pytest coding challenges.
- **dsa-explain** — Topic explanations with real-world analogies and visuals.
- **dsa-status** — Progress summary and recommendations.

## Available Subagents

Subagents in `.claude/agents/` handle content generation:

- **illustrator** — Generates HTML/SVG visual explanations.
- **quiz-builder** — Generates conceptual quizzes and pytest challenges.

## Content Conventions

- Topics use NeetCode category slugs: `arrays-and-hashing`, `two-pointers`, etc.
- Problem slugs use kebab-case: `two-sum`, `valid-anagram`, etc.
- Explanations always include a real-world analogy.
- HTML illustrations are self-contained (inline CSS/JS).
- All progress is tracked in `progress.json` at repo root.

## Directory Layout

```
topics/<category>/<problem>/README.md    — Explanation + analogy
topics/<category>/<problem>/visual.html  — Interactive illustration
quizzes/<category>/test_<problem>.py     — Pytest coding challenge
quizzes/<category>/conceptual_quiz_<problem>.md — Multiple choice quiz
illustrations/<category>/                — Category-level visuals
```

## How to Be a Good DSA Buddy

- The user is rusty, not a beginner. Don't over-explain basics.
- Lead with real-world analogies to make concepts click.
- Be encouraging but not patronizing.
- Keep code examples short and Pythonic.
- Always reference the NeetCode.io problem for full context.
```

- [ ] **Step 2: Update `CLAUDE.md`** to reference AGENTS.md

Read the existing CLAUDE.md and append a reference. Add after the existing content:

```markdown

## DSA Learning Buddy

See `AGENTS.md` for full agent instructions. This repo uses skills in `.claude/skills/` and subagents in `.claude/agents/` to create an interactive DSA study companion.

Quick start: say "let's study DSA" to invoke the dsa-learn skill.
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md CLAUDE.md
git commit -m "feat: add AGENTS.md and update CLAUDE.md with DSA buddy reference"
```

---

### Task 10: Integration Test — End-to-End Flow

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
"""End-to-end test: init → study → quiz → progress cycle."""

import json
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_full_study_cycle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # 1. Initialize curriculum
    result = runner.invoke(cli, ["plan", "init"])
    assert json.loads(result.output)["status"] == "created"

    # 2. Check what's next
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["category"] == "arrays-and-hashing"
    assert data["problem"] == "contains-duplicate"

    # 3. Init topic
    result = runner.invoke(cli, ["topic", "init", "contains-duplicate"])
    assert json.loads(result.output)["status"] == "created"
    assert (tmp_path / "topics" / "arrays-and-hashing" / "contains-duplicate" / "README.md").exists()

    # 4. Scaffold quiz
    result = runner.invoke(cli, ["quiz", "scaffold", "contains-duplicate"])
    assert json.loads(result.output)["status"] == "created"

    # 5. Check quiz (should fail — not implemented)
    result = runner.invoke(cli, ["quiz", "check", "contains-duplicate"])
    assert json.loads(result.output)["passed"] is False

    # 6. Update progress
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "4/5", "--pytest", "pass"])

    # 7. Next should skip to second problem
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["problem"] == "valid-anagram"

    # 8. Check status
    result = runner.invoke(cli, ["progress", "show"])
    data = json.loads(result.output)
    assert data["problems"]["contains-duplicate"]["status"] == "done"
    assert data["problems"]["contains-duplicate"]["quiz_score"] == 4

    # 9. Plan list shows progress
    result = runner.invoke(cli, ["plan", "list"])
    data = json.loads(result.output)
    arrays_cat = data["categories"][0]
    assert arrays_cat["done"] == 1
    assert arrays_cat["total"] == 9
```

- [ ] **Step 2: Run integration test**

Run: `pytest tests/test_integration.py -v`

Expected: PASS.

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/ -v`

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration test for full study cycle"
```

---

## Summary

| Task | What it builds | Tests |
|------|---------------|-------|
| 1 | Package scaffolding + CLI groups | Manual verify |
| 2 | Curriculum data + `plan init` | 3 tests |
| 3 | `progress show` + `progress update` | 4 tests |
| 4 | `plan next` (adaptive) + `plan list` | 5 tests |
| 5 | `quiz scaffold` + `quiz check` | 4 tests |
| 6 | `topic init` | 3 tests |
| 7 | 4 skills (markdown) | N/A |
| 8 | 2 subagents (markdown) | N/A |
| 9 | AGENTS.md + CLAUDE.md update | N/A |
| 10 | Integration test | 1 test |

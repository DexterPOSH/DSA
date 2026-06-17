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

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
    runner.invoke(cli, ["progress", "update", "two-sum", "--status", "in-progress"])
    result = runner.invoke(cli, ["progress", "update", "two-sum", "--quiz-score", "3/5"])
    assert result.exit_code == 0
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["problems"]["two-sum"]["status"] == "in-progress"
    assert progress["problems"]["two-sum"]["quiz_score"] == 3

import json
from click.testing import CliRunner
from dsa_buddy.cli import cli


def test_quiz_scaffold_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "created"
    pytest_path = tmp_path / "quizzes" / "arrays-and-hashing" / "test_two_sum.py"
    assert pytest_path.exists()
    content = pytest_path.read_text()
    assert "def two_sum(" in content
    assert "def test_" in content
    quiz_path = tmp_path / "quizzes" / "arrays-and-hashing" / "conceptual_quiz_two_sum.md"
    assert quiz_path.exists()


def test_quiz_scaffold_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["quiz", "scaffold", "two-sum"])
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
    result = runner.invoke(cli, ["quiz", "check", "two-sum"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["passed"] is False

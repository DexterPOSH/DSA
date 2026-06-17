import json
from click.testing import CliRunner
from sysd_buddy.cli import cli


def test_quiz_scaffold_creates_conceptual_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["quiz", "scaffold", "cap-theorem"])
    assert result.exit_code == 0
    quiz_md = tmp_path / "sysd-quizzes" / "consistency-coordination" / "conceptual_quiz_cap_theorem.md"
    assert quiz_md.exists()
    text = quiz_md.read_text()
    assert "CAP Theorem — Conceptual Quiz" in text
    assert "Ideal answer" in text


def test_quiz_scaffold_unknown_topic_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    data = json.loads(runner.invoke(cli, ["quiz", "scaffold", "nope"]).output)
    assert "error" in data

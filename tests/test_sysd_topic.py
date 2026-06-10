import json
from click.testing import CliRunner
from sysd_buddy.cli import cli


def test_topic_init_creates_readme_in_category(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    result = runner.invoke(cli, ["topic", "init", "cap-theorem"])
    assert result.exit_code == 0
    readme = tmp_path / "sysd-topics" / "consistency-coordination" / "cap-theorem" / "README.md"
    assert readme.exists()
    text = readme.read_text()
    assert "# CAP Theorem" in text
    assert "Real-World Analogy" in text


def test_topic_init_unknown_topic_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    data = json.loads(runner.invoke(cli, ["topic", "init", "nope-not-real"]).output)
    assert "error" in data

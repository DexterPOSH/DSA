import json
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

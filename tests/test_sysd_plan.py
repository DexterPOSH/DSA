import json
from click.testing import CliRunner
from sysd_buddy.cli import cli


def test_plan_init_creates_curriculum_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "init"])
    assert result.exit_code == 0
    path = tmp_path / "sysd-curriculum.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["version"] == 1
    assert [t["slug"] for t in data["tracks"]] == ["building-blocks", "design-problems"]
    bb = data["tracks"][0]
    assert len(bb["categories"]) == 8
    assert bb["categories"][0]["slug"] == "fundamentals-networking"


def test_plan_init_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sysd-curriculum.json").write_text('{"custom": true}')
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "init"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "sysd-curriculum.json").read_text()) == {"custom": True}

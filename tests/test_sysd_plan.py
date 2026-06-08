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


def test_plan_next_first_topic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    data = json.loads(runner.invoke(cli, ["plan", "next"]).output)
    assert data["track"] == "building-blocks"
    assert data["category"] == "fundamentals-networking"
    assert data["topic"] == "dns-request-lifecycle"
    assert "reason" in data


def test_plan_next_gates_design_problems_until_blocks_done(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["progress", "update", "dns-request-lifecycle", "--status", "done"])
    data = json.loads(runner.invoke(cli, ["plan", "next"]).output)
    assert data["track"] == "building-blocks"
    assert data["topic"] != "design-tinyurl"


def test_plan_next_recommends_review_for_low_score(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["progress", "update", "dns-request-lifecycle", "--status", "done"])
    runner.invoke(cli, ["progress", "update", "dns-request-lifecycle", "--quiz-score", "1/5"])
    data = json.loads(runner.invoke(cli, ["plan", "next"]).output)
    assert data["topic"] == "dns-request-lifecycle"
    assert "review" in data["reason"].lower()


def test_plan_list_has_two_tracks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    data = json.loads(runner.invoke(cli, ["plan", "list"]).output)
    assert [t["slug"] for t in data["tracks"]] == ["building-blocks", "design-problems"]
    assert data["tracks"][0]["categories"][0]["done"] == 0

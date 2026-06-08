import json
from click.testing import CliRunner
from sysd_buddy.cli import cli


def test_progress_show_default_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["progress", "show"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"current_track": None, "current_category": None, "topics": {}, "category_summary": {}}


def test_progress_update_status_done_sets_date(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["progress", "update", "cap-theorem", "--status", "done"])
    data = json.loads((tmp_path / "sysd-progress.json").read_text())
    entry = data["topics"]["cap-theorem"]
    assert entry["status"] == "done"
    assert entry["completed_at"] is not None


def test_progress_update_quiz_score_parsed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["progress", "update", "cap-theorem", "--quiz-score", "4/5"])
    entry = json.loads((tmp_path / "sysd-progress.json").read_text())["topics"]["cap-theorem"]
    assert entry["quiz_score"] == 4
    assert entry["quiz_total"] == 5

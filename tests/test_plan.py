import json
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
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["problem"] == "valid-anagram"


def test_plan_next_resurfaces_low_score(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
    runner.invoke(cli, ["progress", "update", "contains-duplicate", "--status", "done", "--quiz-score", "2/5"])
    runner.invoke(cli, ["progress", "update", "valid-anagram", "--status", "done", "--quiz-score", "5/5"])
    result = runner.invoke(cli, ["plan", "next"])
    data = json.loads(result.output)
    assert data["problem"] == "contains-duplicate"
    assert "review" in data["reason"].lower()


def test_plan_next_advances_category(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["plan", "init"])
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

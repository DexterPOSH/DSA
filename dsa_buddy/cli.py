import json
from pathlib import Path

import click


@click.group()
def cli():
    """DSA Learning Buddy — your NeetCode.io study companion."""
    pass


@cli.group()
def plan():
    """Manage your learning plan."""
    pass


@cli.group()
def quiz():
    """Generate and check quizzes."""
    pass


@cli.group()
def progress():
    """Track your learning progress."""
    pass


@cli.group()
def topic():
    """Manage topic content."""
    pass


# --- plan commands ---


@plan.command("init")
def plan_init():
    """Seed curriculum.json with the NeetCode 150 roadmap."""
    from dsa_buddy.plan import init_curriculum

    result = init_curriculum(Path.cwd())
    click.echo(json.dumps(result))


@plan.command("next")
def plan_next_cmd():
    """Get the next recommended problem to study."""
    from dsa_buddy.plan import plan_next

    result = plan_next(Path.cwd())
    click.echo(json.dumps(result, indent=2))


@plan.command("list")
def plan_list_cmd():
    """Show full curriculum with progress."""
    from dsa_buddy.plan import plan_list

    result = plan_list(Path.cwd())
    click.echo(json.dumps(result, indent=2))


# --- progress commands ---


@progress.command("show")
def progress_show():
    """Show current learning progress."""
    from dsa_buddy.progress import show_progress

    result = show_progress(Path.cwd())
    click.echo(json.dumps(result, indent=2))


@progress.command("update")
@click.argument("problem")
@click.option("--status", type=click.Choice(["not-started", "in-progress", "done"]))
@click.option("--quiz-score", help="Score as N/M (e.g. 4/5)")
@click.option("--pytest", "pytest_result", type=click.Choice(["pass", "fail"]))
def progress_update(problem, status, quiz_score, pytest_result):
    """Update progress for a problem."""
    from dsa_buddy.progress import update_progress

    result = update_progress(Path.cwd(), problem, status, quiz_score, pytest_result)
    click.echo(json.dumps(result))


# --- quiz commands ---


@quiz.command("scaffold")
@click.argument("problem")
def quiz_scaffold(problem):
    """Create pytest + conceptual quiz files for a problem."""
    from dsa_buddy.quiz import scaffold_quiz

    result = scaffold_quiz(Path.cwd(), problem)
    click.echo(json.dumps(result))


@quiz.command("check")
@click.argument("problem")
def quiz_check(problem):
    """Run pytest for a problem and return results."""
    from dsa_buddy.quiz import check_quiz

    result = check_quiz(Path.cwd(), problem)
    click.echo(json.dumps(result))


# --- topic commands ---


@topic.command("init")
@click.argument("problem")
def topic_init(problem):
    """Create topic directory with README template."""
    from dsa_buddy.topic import init_topic

    result = init_topic(Path.cwd(), problem)
    click.echo(json.dumps(result))

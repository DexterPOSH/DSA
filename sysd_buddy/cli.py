import json
from pathlib import Path

import click


@click.group()
def cli():
    """SysD Learning Buddy — your system design study companion."""
    pass


@cli.group()
def plan():
    """Manage your learning plan."""
    pass


@cli.group()
def quiz():
    """Generate conceptual quizzes."""
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
    """Seed sysd-curriculum.json with the two-track roadmap."""
    from sysd_buddy.plan import init_curriculum

    click.echo(json.dumps(init_curriculum(Path.cwd())))


@plan.command("next")
def plan_next_cmd():
    """Get the next recommended topic to study."""
    from sysd_buddy.plan import plan_next

    click.echo(json.dumps(plan_next(Path.cwd()), indent=2))


@plan.command("list")
def plan_list_cmd():
    """Show full curriculum with progress."""
    from sysd_buddy.plan import plan_list

    click.echo(json.dumps(plan_list(Path.cwd()), indent=2))


# --- progress commands ---


@progress.command("show")
def progress_show():
    """Show current learning progress."""
    from sysd_buddy.progress import show_progress

    click.echo(json.dumps(show_progress(Path.cwd()), indent=2))


@progress.command("update")
@click.argument("topic")
@click.option("--status", type=click.Choice(["not-started", "in-progress", "done"]))
@click.option("--quiz-score", help="Score as N/M (e.g. 4/5)")
def progress_update(topic, status, quiz_score):
    """Update progress for a topic."""
    from sysd_buddy.progress import update_progress

    click.echo(json.dumps(update_progress(Path.cwd(), topic, status, quiz_score)))


# --- topic commands ---


@topic.command("init")
@click.argument("topic_slug")
def topic_init(topic_slug):
    """Create topic directory with README template."""
    from sysd_buddy.topic import init_topic

    click.echo(json.dumps(init_topic(Path.cwd(), topic_slug)))


# --- quiz commands ---


@quiz.command("scaffold")
@click.argument("topic_slug")
def quiz_scaffold(topic_slug):
    """Create a conceptual quiz markdown file for a topic."""
    from sysd_buddy.quiz import scaffold_quiz

    click.echo(json.dumps(scaffold_quiz(Path.cwd(), topic_slug)))

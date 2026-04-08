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

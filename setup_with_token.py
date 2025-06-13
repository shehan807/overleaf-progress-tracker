#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for linking Overleaf Progress Tracker to a manuscript repository.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import click
import requests
from github import Github


@click.command()
@click.option('--repo-path', prompt='Path to your manuscript repository', 
              help='Path to the local manuscript repository')
@click.option('--github-token', prompt='GitHub Personal Access Token (with repo permissions)', 
              hide_input=True, help='GitHub token for API access')
@click.option('--repo-name', prompt='GitHub repository name (owner/repo)', 
              help='Full name of the GitHub repository (e.g., username/manuscript)')
def setup(repo_path, github_token, repo_name):
    """Setup Overleaf Progress Tracker for a manuscript repository."""
    
    click.echo("\n>>> Setting up Overleaf Progress Tracker...")
    
    # Validate repository path
    repo_path = Path(repo_path).expanduser().resolve()
    if not repo_path.exists():
        click.echo(f"ERROR: Repository path {repo_path} does not exist.", err=True)
        sys.exit(1)
    
    if not (repo_path / '.git').exists():
        click.echo(f"ERROR: {repo_path} is not a git repository.", err=True)
        sys.exit(1)
    
    # Validate GitHub token and repository
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        click.echo(f"SUCCESS: Authenticated with GitHub and found repository: {repo.full_name}")
    except Exception as e:
        click.echo(f"ERROR: Failed to authenticate or find repository: {e}", err=True)
        sys.exit(1)
    
    # Create .github/workflows directory if it doesn't exist
    workflows_dir = repo_path / '.github' / 'workflows'
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy workflow file
    workflow_template = Path(__file__).parent / 'templates' / 'track-progress.yml'
    workflow_dest = workflows_dir / 'track-progress.yml'
    
    if workflow_dest.exists():
        if not click.confirm(f"Workflow file already exists at {workflow_dest}. Overwrite?"):
            click.echo("Skipping workflow file...")
        else:
            shutil.copy2(workflow_template, workflow_dest)
            click.echo(f"SUCCESS: Copied workflow file to {workflow_dest}")
    else:
        shutil.copy2(workflow_template, workflow_dest)
        click.echo(f"SUCCESS: Created workflow file at {workflow_dest}")
    
    # Create data directory for storing progress data
    data_dir = repo_path / '.progress-data'
    data_dir.mkdir(exist_ok=True)
    
    # Initialize progress data file
    progress_file = data_dir / 'progress.json'
    if not progress_file.exists():
        initial_data = {
            "word_counts": [],
            "commits": [],
            "metadata": {
                "repo_name": repo_name,
                "setup_date": str(Path.ctime(Path(__file__))),
                "tracker_version": "1.0.0"
            }
        }
        with open(progress_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        click.echo(f"SUCCESS: Initialized progress data file at {progress_file}")
    
    # Copy scripts directory
    scripts_src = Path(__file__).parent / 'scripts'
    scripts_dest = repo_path / '.github' / 'scripts'
    
    if scripts_dest.exists():
        shutil.rmtree(scripts_dest)
    
    shutil.copytree(scripts_src, scripts_dest)
    click.echo(f"SUCCESS: Copied tracking scripts to {scripts_dest}")
    
    # Create configuration file
    config_file = repo_path / '.progress-tracker.config'
    config_data = {
        "github_token_secret_name": "GITHUB_TOKEN",
        "main_tex_file": "auto",  # Will auto-detect the main .tex file
        "plot_style": {
            "figure_size": [10, 6],
            "line_color": "#2E86AB",
            "annotation_height": 2,
            "categories": {
                "Notes": {"icon": "📝", "color": "#4CAF50"},
                "Milestone": {"icon": "🎯", "color": "#FF9800"},
                "Revisions": {"icon": "✏️", "color": "#F44336"},
                "Progress": {"icon": "📈", "color": "#2196F3"},
                "Fix": {"icon": "🔧", "color": "#9C27B0"},
                "Reference": {"icon": "📚", "color": "#795548"},
                "Other": {"icon": "•", "color": "#607D8B"}
            }
        },
        "texcount_options": "-inc -chinese -japanese -korean -total"
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    click.echo(f"SUCCESS: Created configuration file at {config_file}")
    
    # Update .gitignore
    gitignore_path = repo_path / '.gitignore'
    gitignore_additions = [
        "\n# Progress Tracker",
        ".progress-data/",
        ".progress-tracker.config",
        "progress_plot.png"
    ]
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        for line in gitignore_additions:
            if line.strip() and line not in content:
                content += f"\n{line}"
        
        with open(gitignore_path, 'w') as f:
            f.write(content)
    else:
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(gitignore_additions))
    
    click.echo(f"SUCCESS: Updated .gitignore")
    
    # Instructions for final setup
    click.echo("\n>>> Final Setup Instructions:")
    click.echo(f"1. Navigate to your repository: cd {repo_path}")
    click.echo("2. Add and commit the new files:")
    click.echo("   git add .github/ .progress-tracker.config .gitignore")
    click.echo("   git commit -m 'Add Overleaf Progress Tracker'")
    click.echo("   git push")
    click.echo("\n3. Add your GitHub token as a repository secret:")
    click.echo(f"   - Go to https://github.com/{repo_name}/settings/secrets/actions")
    click.echo("   - Click 'New repository secret'")
    click.echo("   - Name: GITHUB_TOKEN")
    click.echo("   - Value: Your personal access token")
    click.echo("\n4. Make sure your Overleaf project is synced with GitHub")
    click.echo("   - In Overleaf: Menu → Git → Push to GitHub")
    click.echo("\n✨ Setup complete! The tracker will run on every push from Overleaf.")


if __name__ == '__main__':
    setup()
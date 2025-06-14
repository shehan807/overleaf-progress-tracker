#!/usr/bin/env python3
"""
Main script to track LaTeX manuscript progress using texcount.
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import re


def find_main_tex_file(repo_path):
    """Find the main .tex file in the repository."""
    tex_files = list(Path(repo_path).glob("*.tex"))
    
    if not tex_files:
        raise FileNotFoundError("No .tex files found in repository root")
    
    # Look for common main file patterns
    for pattern in ['main.tex', 'manuscript.tex', 'paper.tex', 'article.tex', 'achemso-demo.tex']:
        for tex_file in tex_files:
            if tex_file.name.lower() == pattern:
                return tex_file
    
    # Look for \documentclass in files
    for tex_file in tex_files:
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                if '\\documentclass' in content:
                    return tex_file
        except:
            continue
    
    # Default to first .tex file
    return tex_files[0]


def run_texcount(tex_file, options="-inc -total"):
    """Run texcount on a LaTeX file and return the word count."""
    try:
        cmd = f"texcount {options} {tex_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: texcount returned non-zero exit code: {result.stderr}")
        
        # Parse texcount output
        output = result.stdout
        
        # Look for the total word count with multiple patterns
        patterns = [
            r'Words in text:\s*(\d+)',
            r'Total:\s*(\d+)',
            r'(\d+)\s+words',
            r'(\d+)\s+\+\s+\d+\s+\(.*?\)\s+=\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1) if len(match.groups()) == 1 else match.group(2))
        
        # If no patterns match, try simpler texcount
        simple_cmd = f"texcount -brief {tex_file}"
        simple_result = subprocess.run(simple_cmd, shell=True, capture_output=True, text=True)
        
        # Look for any numbers in the simple output
        numbers = re.findall(r'\b(\d+)\b', simple_result.stdout)
        if numbers:
            return int(numbers[0])
        
        return 0  # Return 0 instead of crashing
        
    except Exception as e:
        print(f"Error running texcount: {e}")
        return 0  # Return 0 instead of crashing


def get_commit_info():
    """Get information about the current commit."""
    try:
        # Get commit hash
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], text=True
        ).strip()
        
        # Get commit message
        commit_message = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B'], text=True
        ).strip()
        
        # Get commit date
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%cI'], text=True
        ).strip()
        
        # Get author
        commit_author = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%an'], text=True
        ).strip()
        
        return {
            'hash': commit_hash[:7],
            'message': commit_message,
            'date': commit_date,
            'author': commit_author
        }
    except Exception as e:
        print(f"Error getting commit info: {e}")
        return None


def parse_commit_category(message):
    """Parse commit message for category."""
    # Look for "Category: message" pattern
    match = re.match(r'^(\w+):\s*(.+)', message)
    if match:
        return match.group(1), match.group(2)
    return "Other", message


def load_progress_data(progress_file):
    """Load existing progress data."""
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {
        "word_counts": [],
        "commits": [],
        "metadata": {}
    }


def save_progress_data(progress_file, data):
    """Save progress data."""
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    with open(progress_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_config(repo_path):
    """Load configuration."""
    config_file = Path(repo_path) / '.progress-tracker.config'
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "plot_style": {
            "figure_size": [10, 6],
            "line_color": "#2E86AB",
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


def create_progress_plot(data, config, output_file):
    """Create a clean progress plot showing word count over time."""
    if not data['word_counts']:
        print("No data to plot yet")
        return
    
    # Extract data
    dates = [datetime.fromisoformat(item['date'].replace('Z', '+00:00')) 
             for item in data['word_counts']]
    word_counts = [item['count'] for item in data['word_counts']]
    
    # Setup plot
    plot_config = config['plot_style']
    fig, ax = plt.subplots(figsize=plot_config['figure_size'])
    
    # Plot word count line
    ax.plot(dates, word_counts, 
            color=plot_config['line_color'], 
            linewidth=2, 
            marker='o', 
            markersize=6,
            label='Word Count')
    
    # Configure axes
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Word Count', fontsize=12)
    ax.set_title('Manuscript Progress Tracking', fontsize=16, fontweight='bold')
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
    plt.xticks(rotation=45)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Calculate statistics
    if len(word_counts) > 1:
        total_change = word_counts[-1] - word_counts[0]
        avg_per_commit = total_change / (len(word_counts) - 1) if len(word_counts) > 1 else 0
        
        # Add statistics text
        stats_text = f"Total Words: {word_counts[-1]:,}\n"
        stats_text += f"Total Change: {total_change:+,}\n"
        stats_text += f"Avg per Commit: {avg_per_commit:+.0f}"
        
        ax.text(0.02, 0.98, stats_text, 
                transform=ax.transAxes, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                verticalalignment='top',
                fontsize=10)
    
    # Clean plot without annotations on the figure
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Progress plot saved to {output_file}")


def generate_commit_bullets(data, config, max_commits=10):
    """Generate bullet points for recent commits."""
    if not data.get('commits'):
        return ""
    
    categories = config['plot_style']['categories']
    bullets = []
    
    # Get recent commits (excluding automated ones)
    recent_commits = []
    for commit in reversed(data['commits'][-max_commits:]):
        if '[skip ci]' not in commit['message'] and 'Update progress tracking' not in commit['message']:
            recent_commits.append(commit)
    
    if not recent_commits:
        return ""
    
    bullets.append("### Recent Progress")
    bullets.append("")
    
    for commit in recent_commits[-10:]:  # Show last 10 non-automated commits
        category, message = parse_commit_category(commit['message'])
        cat_info = categories.get(category, categories['Other'])
        
        # Format commit date
        commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
        date_str = commit_date.strftime('%m/%d/%Y')
        
        # Create bullet point
        bullet = f"- {cat_info['icon']} **{category}**: {message} _{date_str}_"
        bullets.append(bullet)
    
    return "\n".join(bullets) + "\n"


def update_readme(repo_path, plot_file, data, config):
    """Update README.md with the progress plot and commit bullets."""
    readme_path = Path(repo_path) / 'README.md'
    
    # Read existing README
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Marker for progress section
    start_marker = "<!-- PROGRESS-TRACKER-START -->"
    end_marker = "<!-- PROGRESS-TRACKER-END -->"
    
    # Generate bullet points for recent commits
    bullet_points = generate_commit_bullets(data, config)
    
    progress_section = f"""
{start_marker}
## 📊 Manuscript Progress

![Progress Tracking]({plot_file.name})

{bullet_points}

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*
{end_marker}
"""
    
    # Update or add progress section
    if start_marker in content:
        # Replace existing section
        pattern = f"{start_marker}.*?{end_marker}"
        content = re.sub(pattern, progress_section.strip(), content, flags=re.DOTALL)
    else:
        # Add to beginning of README
        if content:
            content = progress_section + "\n" + content
        else:
            content = f"# Manuscript\n\n{progress_section}"
    
    # Write updated README
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"README.md updated")


def main():
    """Main tracking function."""
    # Get repository root
    repo_path = Path.cwd()
    
    # Load configuration
    config = load_config(repo_path)
    
    # Find main tex file
    if config.get('main_tex_file') == 'auto':
        tex_file = find_main_tex_file(repo_path)
    else:
        tex_file = Path(config.get('main_tex_file', 'main.tex'))
    
    print(f"Using LaTeX file: {tex_file}")
    
    # Run texcount
    word_count = run_texcount(tex_file, config.get('texcount_options', '-inc -total'))
    print(f"Current word count: {word_count}")
    
    # Get commit info
    commit_info = get_commit_info()
    
    # Load existing data
    progress_file = repo_path / '.progress-data' / 'progress.json'
    data = load_progress_data(progress_file)
    
    # Add new data point
    if commit_info:
        new_entry = {
            'date': commit_info['date'],
            'count': word_count,
            'commit': commit_info['hash'],
            'author': commit_info['author']
        }
        
        # Only add if different from last entry
        if not data['word_counts'] or data['word_counts'][-1]['count'] != word_count:
            data['word_counts'].append(new_entry)
        
        # Add commit info
        data['commits'].append(commit_info)
    
    # Save updated data
    save_progress_data(progress_file, data)
    
    # Create plot
    plot_file = repo_path / 'progress_plot.png'
    create_progress_plot(data, config, plot_file)
    
    # Update README
    update_readme(repo_path, plot_file, data, config)


if __name__ == '__main__':
    main()
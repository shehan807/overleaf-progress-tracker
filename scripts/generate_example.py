#!/usr/bin/env python3
"""
Generate an example progress plot and bullet points for documentation.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import json


def generate_example_data():
    """Generate example progress data."""
    start_date = datetime.now() - timedelta(days=30)
    
    # Generate word counts with realistic progression
    dates = []
    word_counts = []
    commits = []
    
    base_count = 1000
    for i in range(20):
        date = start_date + timedelta(days=i * 1.5)
        dates.append(date)
        
        # Add some variability
        if i < 5:
            words = base_count + i * 200 + np.random.randint(-50, 100)
        elif i < 10:
            words = word_counts[-1] + np.random.randint(100, 300)
        elif i < 15:
            words = word_counts[-1] + np.random.randint(150, 400)
        else:
            words = word_counts[-1] + np.random.randint(50, 200)
        
        word_counts.append(words)
        
        # Generate varied commit messages
        messages = [
            "Notes: Added introduction and background",
            "Milestone: Completed literature review", 
            "Progress: Wrote methodology section",
            "Notes: Added experimental setup figures",
            "Revisions: Addressed reviewer comments on theory",
            "Fix: Corrected equations in section 3",
            "Reference: Added recent citations",
            "Progress: Finished results analysis",
            "Milestone: Completed first draft",
            "Notes: Added discussion section",
            "Revisions: Updated abstract and conclusions",
            "Fix: Corrected table formatting",
            "Progress: Added appendix materials",
            "Notes: Improved figure captions",
            "Milestone: Submitted for review"
        ]
        
        commits.append({
            'date': date.isoformat(),
            'message': messages[i % len(messages)],
            'hash': f"abc{i:04d}"
        })
    
    return dates, word_counts, commits


def generate_example_bullets(commits):
    """Generate example bullet points for documentation."""
    categories = {
        "Notes": {"icon": "📝", "color": "#4CAF50"},
        "Milestone": {"icon": "🎯", "color": "#FF9800"},
        "Revisions": {"icon": "✏️", "color": "#F44336"},
        "Progress": {"icon": "📈", "color": "#2196F3"},
        "Fix": {"icon": "🔧", "color": "#9C27B0"},
        "Reference": {"icon": "📚", "color": "#795548"},
        "Other": {"icon": "•", "color": "#607D8B"}
    }
    
    bullets = ["### Recent Progress", ""]
    
    # Show last 8 commits
    for commit in commits[-8:]:
        category = commit['message'].split(':')[0]
        message = commit['message'].split(':', 1)[1].strip()
        
        cat_info = categories.get(category, categories['Other'])
        commit_date = datetime.fromisoformat(commit['date'])
        date_str = commit_date.strftime('%m/%d/%Y')
        
        bullet = f"- {cat_info['icon']} **{category}**: {message} _{date_str}_"
        bullets.append(bullet)
    
    return "\n".join(bullets)


def create_example_plot():
    """Create a clean example progress plot."""
    dates, word_counts, commits = generate_example_data()
    
    # Setup plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot word count line
    ax.plot(dates, word_counts, 
            color='#2E86AB', 
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
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics
    total_change = word_counts[-1] - word_counts[0]
    avg_per_commit = total_change / (len(word_counts) - 1)
    
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
    plt.savefig('../docs/example_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Example plot saved to docs/example_plot.png")
    
    # Generate and save example bullet points
    bullets = generate_example_bullets(commits)
    with open('../docs/example_bullets.md', 'w') as f:
        f.write(f"""# Example Progress Section

![Progress Tracking](example_plot.png)

{bullets}

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*
""")
    
    print("Example bullet points saved to docs/example_bullets.md")


if __name__ == '__main__':
    create_example_plot()
#!/usr/bin/env python3
"""
Generate an example progress plot for documentation.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
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
        
        # Generate commit messages
        if i % 3 == 0:
            commits.append({
                'date': date.isoformat(),
                'message': f"Milestone: Completed section {i//3 + 1}",
                'hash': f"abc{i:04d}"
            })
        elif i % 3 == 1:
            commits.append({
                'date': date.isoformat(),
                'message': f"Notes: Added figures and tables",
                'hash': f"def{i:04d}"
            })
        else:
            commits.append({
                'date': date.isoformat(),
                'message': f"Revisions: Addressed feedback on methodology",
                'hash': f"ghi{i:04d}"
            })
    
    return dates, word_counts, commits


def create_example_plot():
    """Create an example progress plot."""
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
    
    # Add annotations area
    y_min, y_max = ax.get_ylim()
    annotation_height = (y_max - y_min) * 0.3
    annotation_y_start = y_min - annotation_height
    
    ax.set_ylim(annotation_y_start, y_max * 1.05)
    
    # Add annotation background
    ax.add_patch(Rectangle((mdates.date2num(dates[0]) - 0.5, annotation_y_start),
                          mdates.date2num(dates[-1]) - mdates.date2num(dates[0]) + 1,
                          annotation_height,
                          facecolor='#f5f5f5',
                          edgecolor='none',
                          zorder=0))
    
    # Categories
    categories = {
        "Notes": {"icon": "📝", "color": "#4CAF50"},
        "Milestone": {"icon": "🎯", "color": "#FF9800"},
        "Revisions": {"icon": "✏️", "color": "#F44336"}
    }
    
    # Add some example annotations
    annotation_y = annotation_y_start + annotation_height * 0.8
    
    for i, commit in enumerate(commits[-6:]):  # Show last 6 commits
        category = commit['message'].split(':')[0]
        message = commit['message'].split(':', 1)[1].strip()
        
        cat_info = categories.get(category, {"icon": "•", "color": "#607D8B"})
        commit_date = datetime.fromisoformat(commit['date'])
        
        annotation_text = f"{cat_info['icon']} {message[:30]}..."
        date_text = commit_date.strftime('%m/%d')
        
        y_pos = annotation_y - (i % 2) * annotation_height * 0.15
        
        ax.text(mdates.date2num(commit_date), y_pos,
               f"{annotation_text} ({date_text})",
               fontsize=8,
               color=cat_info['color'],
               ha='center',
               va='top',
               bbox=dict(boxstyle='round,pad=0.3', 
                       facecolor='white', 
                       edgecolor=cat_info['color'],
                       alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('../docs/example_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Example plot saved to docs/example_plot.png")


if __name__ == '__main__':
    create_example_plot()
# Troubleshooting Guide

## Common Issues and Solutions

### 1. Setup Issues

#### "ModuleNotFoundError: No module named 'matplotlib'"
**Solution**: Install the required dependencies:
```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

#### "Permission denied" when running setup.py
**Solution**: Make the script executable:
```bash
chmod +x setup.py
python setup.py
```

### 2. GitHub Actions Issues

#### Workflow not triggering
**Possible causes**:
- Check if the workflow file is in `.github/workflows/`
- Ensure you're pushing to the correct branch (main/master)
- Verify GitHub Actions are enabled for your repository

#### "GITHUB_TOKEN: unbound variable"
**Solution**: Add your GitHub token as a repository secret:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GITHUB_TOKEN`
4. Value: Your personal access token

### 3. Word Counting Issues

#### "texcount: command not found" (local testing)
**Solution**: Install texcount locally:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-extra-utils

# macOS with Homebrew
brew install texlive

# Windows
# Install MiKTeX or TeX Live
```

#### Word count seems incorrect
**Check**:
- Is your main .tex file being detected correctly?
- Are all included files in the repository?
- Try adjusting texcount options in `.progress-tracker.config`

**Debug command**:
```bash
texcount -inc -total your_file.tex
```

### 4. Plot Generation Issues

#### Plot not showing annotations
**Check**:
- Commit message format: `Category: message`
- Supported categories in configuration
- Maximum 10 recent commits are shown

#### Plot looks distorted
**Solution**: Adjust plot settings in `.progress-tracker.config`:
```json
{
  "plot_style": {
    "figure_size": [12, 8],  // Increase size
    "annotation_height": 3    // More space for annotations
  }
}
```

### 5. Repository Issues

#### Changes not appearing in README
**Check**:
- Is the workflow completing successfully?
- Check the Actions tab for error logs
- Ensure README.md exists and has proper markers

#### Merge conflicts with progress updates
**Solution**: Add `[skip ci]` to manual commits to avoid triggering the workflow:
```bash
git commit -m "Manual update [skip ci]"
```

## Debug Mode

### Running locally for debugging

1. Navigate to your manuscript repository:
```bash
cd /path/to/your/manuscript
```

2. Set up environment:
```bash
export GITHUB_TOKEN="your_token_here"
```

3. Run with verbose output:
```bash
python3 .github/scripts/track_progress.py --verbose
```

### Checking workflow logs

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Click on a workflow run
4. Click on "track-progress" job
5. Expand each step to see detailed logs

## Getting Help

If you're still experiencing issues:

1. Check existing [issues](https://github.com/yourusername/overleaf-progress-tracker/issues)
2. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Your configuration file (remove sensitive data)
   - Workflow logs

## FAQ

**Q: Can I track multiple .tex files?**
A: Yes, texcount will include all files referenced with `\input` or `\include`

**Q: How often should I sync from Overleaf?**
A: The tracker runs on every push, so sync as often as you like

**Q: Can I customize the plot appearance?**
A: Yes, edit the `plot_style` section in `.progress-tracker.config`

**Q: Will this count bibliography, captions, etc.?**
A: By default, texcount includes text in captions but excludes bibliography. Adjust with `texcount_options`
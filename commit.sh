#!/bin/bash

# Navigate to your folder
cd /path/to/your/folder

# Initialize Git if needed
if [ ! -d ".git" ]; then
  git init
fi

# Configure branch name (modern repos use 'main')
DEFAULT_BRANCH="main"

# Create initial commit if none exists
if [ -z "$(git branch --list)" ]; then
  echo "Creating initial commit..."
  git add .
  git commit -m "Initial commit"
  git branch -M $DEFAULT_BRANCH
fi

# Detect existing branch name
CURRENT_BRANCH=$(git branch --show-current)

# Set up LFS
git lfs install
git lfs track "*.zip" "*.pdf" "*.dat" "*.bin"
git add .gitattributes
git commit -m "Add LFS tracking" 2>/dev/null || true

# Add all files
git add .
git commit -m "Add project files" 2>/dev/null || true

# Set remote
# Auto-configure SSH if HTTPS fails
git remote set-url origin git@github.com:RustT883/AntivirGraphRAG.git 2>/dev/null || true

# Push with branch creation
git push -u origin $CURRENT_BRANCH

# If still failing, try forcing branch creation
if [ $? -ne 0 ]; then
  echo "Creating remote branch..."
  git push -u origin HEAD
fi

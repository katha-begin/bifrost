#!/bin/bash
echo "Initializing Git repository for Bifrost..."

# Initialize the repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit of Bifrost Animation Asset Management System"

echo ""
echo "Repository initialized locally!"
echo ""
echo "To push to GitHub, run these commands:"
echo ""
echo "git remote add origin https://github.com/YOUR_USERNAME/bifrost.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "Make sure to replace YOUR_USERNAME with your GitHub username."
echo ""

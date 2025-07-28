#!/bin/bash

# Render Deployment Script for AI Presentation Service
# This script helps prepare and deploy the service to Render

set -e

echo "🚀 AI Presentation Service - Render Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not found. Please initialize git first:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

# Check if remote is configured
if ! git remote get-url origin > /dev/null 2>&1; then
    print_warning "No remote repository configured. Please add your GitHub repository:"
    echo "  git remote add origin https://github.com/yourusername/your-repo.git"
    exit 1
fi

# Check required files
echo "📋 Checking required files..."

required_files=(
    "render.yaml"
    "requirements.txt"
    "gunicorn.conf.py"
    "ppt_flask.py"
    "modules/pptfinal.py"
    "modules/s3_service.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    print_warning "You're not on main/master branch. Current branch: $current_branch"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes:"
    git status --short
    
    read -p "Commit changes before deploying? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_warning "Deploying with uncommitted changes..."
    else
        echo "Enter commit message:"
        read commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Deploy to Render"
        fi
        git add .
        git commit -m "$commit_message"
        print_status "Changes committed"
    fi
fi

# Push to remote
echo "📤 Pushing to remote repository..."
git push origin main
print_status "Code pushed to remote"

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. Go to https://dashboard.render.com/"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Connect your GitHub repository"
echo "4. Select this repository"
echo "5. Render will automatically detect render.yaml"
echo ""
echo "6. After deployment, configure environment variables:"
echo "   - OPENROUTER_API_KEY (required)"
echo "   - ALLOWED_ORIGINS (optional)"
echo "   - AWS_* variables (optional, for S3)"
echo ""
echo "7. Update your frontend environment:"
echo "   VITE_PPT_API_URL=https://your-service-name.onrender.com"
echo ""
echo "8. Test the deployment:"
echo "   curl https://your-service-name.onrender.com/health"
echo ""

print_status "Deployment preparation complete!"
print_warning "Remember to set your OPENROUTER_API_KEY in Render dashboard" 
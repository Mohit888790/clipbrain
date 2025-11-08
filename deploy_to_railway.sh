#!/bin/bash

# ClipBrain Railway Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "🚂 ClipBrain Railway Deployment"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${BLUE}Initializing git repository...${NC}"
    git init
    git branch -M main
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found!${NC}"
    echo "Install it with: npm i -g @railway/cli"
    echo "Or deploy via GitHub (see RAILWAY_QUICK_DEPLOY.md)"
    exit 1
fi

# Check if logged in to Railway
echo -e "${BLUE}Checking Railway authentication...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${BLUE}Please login to Railway:${NC}"
    railway login
fi

# Commit any changes
echo -e "${BLUE}Committing changes...${NC}"
git add .
git commit -m "Deploy to Railway" || echo "No changes to commit"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with your configuration"
    exit 1
fi

# Deploy to Railway
echo -e "${BLUE}Deploying to Railway...${NC}"
railway up

# Set environment variables from .env
echo -e "${BLUE}Setting environment variables...${NC}"
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ $key =~ ^#.*$ ]] && continue
    [[ -z $key ]] && continue
    
    # Remove quotes from value
    value=$(echo $value | sed -e 's/^"//' -e 's/"$//')
    
    echo "Setting $key..."
    railway variables set "$key=$value"
done < .env

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Check deployment: railway open"
echo "2. View logs: railway logs"
echo "3. Get URL: railway domain"
echo ""
echo "To deploy worker:"
echo "1. Create new service in Railway dashboard"
echo "2. Set start command: cd backend && python workers/worker.py"
echo "3. Add same environment variables"

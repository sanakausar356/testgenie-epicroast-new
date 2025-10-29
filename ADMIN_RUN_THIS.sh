#!/bin/bash
# Admin: Run this script to deploy Ibtasam's changes to production

echo "🚀 Deploying TestGenie Updates to Production"
echo "=============================================="
echo ""

# Navigate to your local repository
echo "📍 Step 1: Navigate to repository..."
# ADMIN: Update this path to your local repo path
cd ~/path/to/summervibe-testgenie-epicroast || { echo "❌ Error: Repository path not found!"; exit 1; }

echo "✅ Current directory: $(pwd)"
echo ""

# Check if remote already exists
echo "📍 Step 2: Add Ibtasam's repository..."
if git remote get-url ibtasam &> /dev/null; then
    echo "✅ Remote 'ibtasam' already exists"
else
    git remote add ibtasam https://github.com/Ibtasamali01/TestGenie.git
    echo "✅ Added remote 'ibtasam'"
fi

echo ""
echo "📍 Step 3: Fetch latest changes from Ibtasam..."
git fetch ibtasam
echo "✅ Fetched successfully"
echo ""

# Show what will be merged
echo "📍 Step 4: Preview changes..."
echo "Commits to be merged:"
git log HEAD..ibtasam/main --oneline | head -20
echo ""

# Merge changes
echo "📍 Step 5: Merging changes..."
git merge ibtasam/main -m "Merge latest updates from Ibtasam: Enhanced AC suggestions, Jira status integration, bug fixes"

if [ $? -eq 0 ]; then
    echo "✅ Merge successful!"
    echo ""
    
    echo "📍 Step 6: Pushing to origin (triggers Vercel deployment)..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Deployment initiated!"
        echo "✅ Changes pushed to GitHub"
        echo "✅ Vercel will auto-deploy in 2-3 minutes"
        echo "🔗 URL: https://summervibe-testgenie-epicroast.vercel.app/"
        echo ""
        echo "Changes deployed:"
        echo "  ✅ Enhanced AC suggestions (8-12 clauses, professional)"
        echo "  ✅ Jira status integration"
        echo "  ✅ Cleaner output formatting"
        echo "  ✅ Bug fixes and improvements"
    else
        echo "❌ Error pushing to origin. Check permissions."
        exit 1
    fi
else
    echo "❌ Merge failed. Resolve conflicts manually:"
    echo "   git status"
    echo "   # Fix conflicts in files"
    echo "   git add ."
    echo "   git commit"
    echo "   git push origin main"
    exit 1
fi


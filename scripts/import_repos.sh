#!/bin/bash

# AutoRebase Repository Import Script
# Update the variables below with your actual repository URLs and tags

# Repository URLs and tags - UPDATE THESE
BASE_REPO_URL="https://github.com/your-org/base-repo.git"
FEATURE_REPO_URL="https://github.com/your-org/feature-repo.git"
BASE_0_TAG="base-0"
BASE_1_TAG="base-1"
FEATURE_0_TAG="feature-0"

# Data directory
DATA_DIR="data/repos"

echo "AutoRebase Repository Importer"
echo "=============================="
echo "⚠️  Please update the repository URLs and tags in this script before running"
echo ""

# Check if user wants to proceed
read -p "Do you want to proceed with the import? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Import cancelled."
    exit 0
fi

# Create data directory
mkdir -p "$DATA_DIR"

echo "Starting repository import..."

# Function to clone repository
clone_repo() {
    local repo_url="$1"
    local target_dir="$2"
    local tag="$3"
    
    echo "Cloning $repo_url to $target_dir"
    
    # Remove existing directory
    if [ -d "$target_dir" ]; then
        echo "Removing existing directory: $target_dir"
        rm -rf "$target_dir"
    fi
    
    # Clone repository
    if git clone "$repo_url" "$target_dir"; then
        echo "✅ Successfully cloned $repo_url"
        
        # Checkout specific tag if provided
        if [ -n "$tag" ]; then
            cd "$target_dir"
            if git checkout "$tag"; then
                echo "✅ Checked out tag: $tag"
            else
                echo "❌ Failed to checkout tag: $tag"
                return 1
            fi
            cd - > /dev/null
        fi
        
        return 0
    else
        echo "❌ Failed to clone $repo_url"
        return 1
    fi
}

# Import repositories
echo ""
echo "Importing Base-0 repository..."
clone_repo "$BASE_REPO_URL" "$DATA_DIR/base-0" "$BASE_0_TAG"
BASE_0_SUCCESS=$?

echo ""
echo "Importing Base-1 repository..."
clone_repo "$BASE_REPO_URL" "$DATA_DIR/base-1" "$BASE_1_TAG"
BASE_1_SUCCESS=$?

echo ""
echo "Importing Feature-0 repository..."
clone_repo "$FEATURE_REPO_URL" "$DATA_DIR/feature-0" "$FEATURE_0_TAG"
FEATURE_0_SUCCESS=$?

# Report results
echo ""
echo "=============================="
echo "IMPORT RESULTS:"
echo "=============================="
echo "Base-0 repository: $([ $BASE_0_SUCCESS -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
echo "Base-1 repository: $([ $BASE_1_SUCCESS -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
echo "Feature-0 repository: $([ $FEATURE_0_SUCCESS -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"

if [ $BASE_0_SUCCESS -eq 0 ] && [ $BASE_1_SUCCESS -eq 0 ] && [ $FEATURE_0_SUCCESS -eq 0 ]; then
    echo ""
    echo "🎉 All repositories imported successfully!"
    
    # List imported repositories
    echo ""
    echo "=============================="
    echo "IMPORTED REPOSITORIES:"
    echo "=============================="
    
    for repo_dir in "$DATA_DIR"/*; do
        if [ -d "$repo_dir" ]; then
            repo_name=$(basename "$repo_dir")
            echo ""
            echo "📁 $repo_name:"
            
            # Get latest commit
            cd "$repo_dir"
            latest_commit=$(git log --oneline -1)
            echo "   Latest commit: $latest_commit"
            
            # Get current tag or branch
            current_tag=$(git describe --tags --exact-match HEAD 2>/dev/null)
            current_branch=$(git branch --show-current)
            
            if [ -n "$current_tag" ]; then
                echo "   Current tag: $current_tag"
            elif [ -n "$current_branch" ]; then
                echo "   Current branch: $current_branch"
            fi
            
            # Count files
            file_count=$(find . -type f | wc -l)
            echo "   Files: $file_count"
            
            cd - > /dev/null
        fi
    done
else
    echo ""
    echo "❌ Some repositories failed to import. Check the errors above."
    exit 1
fi

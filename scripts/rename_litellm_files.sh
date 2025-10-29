#!/bin/bash

# Script to rename all files and directories containing "litellm" to "remodl"
# Run from the root of remodl-sdk directory

set -e

echo "🔍 Finding files and directories with 'litellm' in their names..."

# First, find all files and directories (excluding .git)
# We need to process deepest paths first to avoid renaming parent dirs before children
find . -depth -name "*litellm*" -not -path "./.git/*" -not -path "./scripts/*" | while read -r path; do
    # Skip if path doesn't exist (might have been renamed already as parent)
    if [ ! -e "$path" ]; then
        continue
    fi
    
    # Get directory and filename
    dir=$(dirname "$path")
    filename=$(basename "$path")
    
    # Create new name by replacing litellm with remodl
    new_filename=$(echo "$filename" | sed 's/litellm/remodl/g')
    new_path="$dir/$new_filename"
    
    # Only rename if the name actually changed
    if [ "$filename" != "$new_filename" ]; then
        echo "  Renaming: $path → $new_path"
        
        # Use git mv if the file is tracked, otherwise use regular mv
        if git ls-files --error-unmatch "$path" > /dev/null 2>&1; then
            git mv "$path" "$new_path"
        else
            mv "$path" "$new_path"
        fi
    fi
done

echo "✅ File and directory renaming complete!"
echo ""
echo "📝 Summary of renames:"
git status --short | grep "^R" | head -20


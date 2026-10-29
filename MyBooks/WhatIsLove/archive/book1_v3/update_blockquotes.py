#!/usr/bin/env python3
"""
Script to update all blockquotes with HTML span author elements to LaTeX format
"""

import os
import re
import glob

def update_blockquote_in_content(content):
    """Update blockquotes with HTML span author elements to LaTeX format"""
    
    # Pattern to match blockquotes with HTML span author elements
    pattern = r'<div class="blockquote"[^>]*>\s*([^<]+?)\s*<span class="author"[^>]*>([^<]+?)</span>\s*</div>'
    
    def replace_blockquote(match):
        quote_text = match.group(1).strip()
        author_text = match.group(2).strip()
        
        # Clean up the author text - remove any existing dashes
        author_text = author_text.lstrip('—').lstrip('-').strip()
        
        # Return the new format
        return f'<div class="blockquote">\n{quote_text}\n\n\\hfill\\small — {author_text}\n</div>'
    
    # Apply the replacement
    updated_content = re.sub(pattern, replace_blockquote, content, flags=re.DOTALL)
    
    return updated_content

def main():
    # Get all markdown files in the chapters directory
    chapters_dir = "/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/chapters"
    md_files = glob.glob(os.path.join(chapters_dir, "*.md"))
    
    updated_files = []
    
    for file_path in md_files:
        print(f"Processing {os.path.basename(file_path)}...")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update blockquotes
        updated_content = update_blockquote_in_content(content)
        
        # Check if any changes were made
        if content != updated_content:
            # Write the updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            updated_files.append(os.path.basename(file_path))
            print(f"  ✓ Updated {os.path.basename(file_path)}")
        else:
            print(f"  - No changes needed for {os.path.basename(file_path)}")
    
    print(f"\nSummary: Updated {len(updated_files)} files")
    for file in updated_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main()

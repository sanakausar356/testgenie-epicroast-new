#!/usr/bin/env python3
"""
Script to remove all user story references from the analysis instructions
"""

import re

def remove_user_story_references():
    """Remove all user story references from groomroom/core.py"""
    
    # Read the file
    with open('groomroom/core.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove user story references from analysis instructions
    patterns_to_remove = [
        # Remove user story lines from DOR requirements
        r'- \*\*User Story\*\*: .*\n',
        # Remove user story lines from card type validation
        r'- \*\*User Story\*\*: Must be tied to Features.*\n',
        # Remove user story detection from AI understanding
        r'- Identify if user story follows agile template.*\n',
        # Remove user story from actionable level description
        r'highlight only items that directly map to user stories or acceptance criteria',
        # Remove user story from checklist
        r'- \*\*Check User Story Template\*\*.*\n',
        r'- \[ \] \*\*Card\*\*: Well-written user story\n',
        # Remove user story from field names
        r"'user story', ",
        # Remove user story from enhanced analysis
        r'1\. \*\*User Story Detection\*\*:.*\n',
        # Remove user story from scoring
        r'Fixes scoring penalties when user story and figma are actually present',
        r'# Analyze DOR requirements with enhanced user story detection',
    ]
    
    # Apply all patterns
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Remove user story from acceptance criteria indicators
    content = re.sub(r"'user story', ", '', content)
    
    # Write the file back
    with open('groomroom/core.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed user story references from analysis instructions")

if __name__ == "__main__":
    remove_user_story_references() 
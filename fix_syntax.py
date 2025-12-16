#!/usr/bin/env python3
import os
import re

def fix_syntax_errors(directory):
    """Fix unterminated triple quotes in Python files"""
    for root, dirs, files in os.walk(directory):
        # Skip thirdlib directory for now
        if 'thirdlib' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Remove lines that are just triple quotes at the start
                    lines = content.split('\n')
                    new_lines = []

                    for i, line in enumerate(lines):
                        # If it's just triple quotes and appears early in the file (first 10 lines)
                        if line.strip() == "'''" and i < 10:
                            continue
                        new_lines.append(line)

                    new_content = '\n'.join(new_lines)

                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed: {filepath}")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_syntax_errors("/home/sondt/dirmap")
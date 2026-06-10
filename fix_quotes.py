#!/usr/bin/env python3
"""Fix smart quotes in PowerShell script"""

# Read the file
with open('run_dashboard.ps1', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace smart quotes with regular quotes
content = content.replace('"', '"')  # Left double quote
content = content.replace('"', '"')  # Right double quote
content = content.replace(''', "'")  # Left single quote
content = content.replace(''', "'")  # Right single quote

# Write back
with open('run_dashboard.ps1', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed smart quotes in run_dashboard.ps1")

# Made with Bob

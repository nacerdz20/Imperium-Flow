#!/usr/bin/env python3
"""
Worker Template Migrator
Reads .md templates from old repo and saves them as Python string constants or config files.
"""

import os
import glob
import logging

def migrate_templates():
    OLD_PATH = "/home/nacer_00/Documents/cloude ai agent/conductor-orchestrator-superpowers/skills/worker-templates/*.md"
    NEW_PATH = "/home/nacer_00/Documents/cloude ai agent/zouaizia-nacer-orchestrator/src/config/worker_templates.py"
    
    templates = {}
    
    # Read files
    for file_path in glob.glob(OLD_PATH):
        filename = os.path.basename(file_path)
        role_name = filename.replace(".template.md", "").replace("-", "_").upper()
        
        with open(file_path, "r") as f:
            content = f.read()
            # Clean Frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
            
            templates[role_name] = content
            print(f"✅ Loaded {role_name}")

    # Write to Python config file
    with open(NEW_PATH, "w") as f:
        f.write('"""\nWorker Role Templates\nAuto-generated from legacy markdown files.\n"""\n\n')
        for role, text in templates.items():
            # Safe string formatting
            safe_text = text.replace('"""', '\\"\\"\\"')
            f.write(f'{role} = """\n{safe_text}\n"""\n\n')
            
    print(f"✨ Saved {len(templates)} templates to {NEW_PATH}")

if __name__ == "__main__":
    migrate_templates()

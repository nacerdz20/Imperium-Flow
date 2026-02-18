#!/usr/bin/env python3
"""
Bulk Skill Import Script
Reads all skills from the original repository and saves them to the new system.
"""

from src.core.skill_importer import SkillImporter
from src.core.skills_registry import SkillsRegistry
import os
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # المسار إلى مستودع المهارات القديم
    # سنفترض أنه في المجلد المجاور كما هو واضح في الـ workspace
    OLD_REPO_PATH = "/home/nacer_00/Documents/cloude ai agent/conductor-orchestrator-superpowers/skills"
    
    if not os.path.exists(OLD_REPO_PATH):
        print(f"❌ Path not found: {OLD_REPO_PATH}")
        return

    importer = SkillImporter(OLD_REPO_PATH)
    registry = SkillsRegistry()
    
    imported_skills = importer.import_all_skills()
    
    print(f"\n✨ Successfully imported {len(imported_skills)} skills into memory!")
    
    # في الواقع، يجب حفظ هذه المهارات في قاعدة بيانات أو ملفات JSON
    # هنا سنقوم بتجربة واحدة للتأكد
    
    if "writing-plans" in imported_skills:
        skill = imported_skills["writing-plans"]
        print(f"\n📜 Sample Skill: {skill.name}")
        print(f"Prompt Length: {len(skill.get_prompt())} chars")
        print("Preview:\n" + skill.get_prompt()[:200] + "...")

    # حفظ المهارات (Mock save)
    # يمكننا لاحقاً إضافتها للـ SkillsRegistry بشكل دائم

if __name__ == "__main__":
    main()

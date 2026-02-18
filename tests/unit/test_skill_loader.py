"""
Tests for SkillLoader and DynamicSkill — skill loading from filesystem.
Targets: skill_loader.py (0% → 80%+)
"""

import os
import tempfile
import pytest
from src.core.skill_loader import SkillLoader, DynamicSkill


class TestDynamicSkill:
    """Test the DynamicSkill data class."""

    def test_init(self):
        skill = DynamicSkill(name="test-skill", instructions="Do X then Y")
        assert skill.name == "test-skill"
        assert skill.instructions == "Do X then Y"

    def test_get_prompt_returns_instructions(self):
        skill = DynamicSkill(name="planning", instructions="Step 1: Plan")
        assert skill.get_prompt() == "Step 1: Plan"

    def test_get_prompt_empty(self):
        skill = DynamicSkill(name="empty", instructions="")
        assert skill.get_prompt() == ""


class TestSkillLoaderInit:
    """Test SkillLoader initialization."""

    def test_init_stores_path(self):
        loader = SkillLoader("/some/path")
        assert loader.skills_dir == "/some/path"


class TestLoadAllSkills:
    """Test loading skills from the filesystem."""

    def test_load_from_nonexistent_dir(self):
        loader = SkillLoader("/nonexistent/path")
        result = loader.load_all_skills()
        assert result == {}

    def test_load_empty_dir(self, tmp_path):
        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()
        assert result == {}

    def test_load_single_skill(self, tmp_path):
        # Create skill directory with SKILL.md
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill\n\nDo something great!")

        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()

        assert "my-skill" in result
        assert isinstance(result["my-skill"], DynamicSkill)
        assert "Do something great" in result["my-skill"].get_prompt()

    def test_load_multiple_skills(self, tmp_path):
        for name in ["alpha", "beta", "gamma"]:
            d = tmp_path / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {name}\n\nInstructions for {name}")

        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()

        assert len(result) == 3
        assert "alpha" in result
        assert "beta" in result
        assert "gamma" in result

    def test_skips_files_not_directories(self, tmp_path):
        (tmp_path / "not-a-dir.txt").write_text("I'm a file")

        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()
        assert len(result) == 0

    def test_skips_dirs_without_skill_md(self, tmp_path):
        (tmp_path / "no-skill").mkdir()
        (tmp_path / "no-skill" / "README.md").write_text("Not a skill file")

        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()
        assert len(result) == 0

    def test_handles_read_error_gracefully(self, tmp_path):
        skill_dir = tmp_path / "broken"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("content")
        # Make it unreadable
        os.chmod(str(skill_file), 0o000)

        loader = SkillLoader(str(tmp_path))
        result = loader.load_all_skills()
        # Should handle error gracefully
        assert "broken" not in result

        # Cleanup: restore permissions for tmp_path cleanup
        os.chmod(str(skill_file), 0o644)


class TestCleanMarkdown:
    """Test the _clean_markdown method."""

    def test_removes_yaml_frontmatter(self):
        loader = SkillLoader("/tmp")
        content = "---\nname: test\ndescription: hello\n---\n\n# The Real Content"
        result = loader._clean_markdown(content)
        assert result == "# The Real Content"

    def test_no_frontmatter_returns_original(self):
        loader = SkillLoader("/tmp")
        content = "# Just Content\n\nNo frontmatter here"
        result = loader._clean_markdown(content)
        assert result == content

    def test_frontmatter_only_one_separator(self):
        loader = SkillLoader("/tmp")
        content = "---\njust one separator"
        result = loader._clean_markdown(content)
        assert content == result

    def test_empty_content(self):
        loader = SkillLoader("/tmp")
        assert loader._clean_markdown("") == ""

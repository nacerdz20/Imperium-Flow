"""
Tests for Imperium Memory — Store, Recall, Cross-Agent, Persistence.
"""

import pytest
import json
import os
from src.core.memory import ImperiumMemory, MemoryEntry


class TestMemoryEntry:
    """Test MemoryEntry dataclass."""

    def test_defaults(self):
        entry = MemoryEntry(
            agent_name="codebot",
            category="patterns",
            key="extract_method",
            value={"steps": ["identify", "extract"]},
        )
        assert entry.success_rate == 1.0
        assert entry.access_count == 0

    def test_to_dict(self):
        entry = MemoryEntry(
            agent_name="testbot",
            category="coverage",
            key="login_tests",
            value={"coverage": 95},
            success_rate=0.95,
        )
        d = entry.to_dict()
        assert d["agent_name"] == "testbot"
        assert d["category"] == "coverage"
        assert d["value"]["coverage"] == 95
        assert "created_at" in d
        assert "last_accessed" in d


class TestImperiumMemory:
    """Test ImperiumMemory store/recall operations."""

    def test_store_and_recall(self):
        mem = ImperiumMemory()
        mem.store_memory("codebot", "patterns", "singleton", {"type": "creational"})
        result = mem.recall("codebot", "patterns", "singleton")
        assert result is not None
        assert result["type"] == "creational"

    def test_recall_nonexistent_returns_none(self):
        mem = ImperiumMemory()
        assert mem.recall("unknown", "x", "y") is None

    def test_recall_updates_access_count(self):
        mem = ImperiumMemory()
        mem.store_memory("bot", "cat", "key", {"data": 1})
        mem.recall("bot", "cat", "key")
        mem.recall("bot", "cat", "key")
        entry = mem.store["bot"]["cat"]["key"]
        assert entry.access_count == 2

    def test_recall_by_category(self):
        mem = ImperiumMemory()
        mem.store_memory("bot", "fixes", "fix1", {"desc": "null check"}, success_rate=0.9)
        mem.store_memory("bot", "fixes", "fix2", {"desc": "timeout"}, success_rate=0.5)
        mem.store_memory("bot", "fixes", "fix3", {"desc": "retry"}, success_rate=0.8)

        results = mem.recall_by_category("bot", "fixes", min_success_rate=0.7)
        assert len(results) == 2
        # Should be sorted by success_rate descending
        assert results[0]["success_rate"] >= results[1]["success_rate"]

    def test_recall_by_category_empty(self):
        mem = ImperiumMemory()
        results = mem.recall_by_category("bot", "nonexistent")
        assert results == []

    def test_recall_cross_agent(self):
        mem = ImperiumMemory()
        mem.store_memory("codebot", "best_practices", "tdd", {"rule": "test first"}, 0.95)
        mem.store_memory("testbot", "best_practices", "coverage", {"min": 90}, 0.85)
        mem.store_memory("designbot", "best_practices", "a11y", {"wcag": "AA"}, 0.6)

        results = mem.recall_cross_agent("best_practices", min_success_rate=0.7)
        assert len(results) == 2  # designbot filtered out (0.6 < 0.7)
        assert results[0]["success_rate"] >= results[1]["success_rate"]

    def test_update_success_rate(self):
        mem = ImperiumMemory()
        mem.store_memory("bot", "patterns", "retry", {"delay": 1}, success_rate=0.5)
        updated = mem.update_success_rate("bot", "patterns", "retry", 0.9)
        assert updated is True
        entry = mem.store["bot"]["patterns"]["retry"]
        assert entry.success_rate == 0.9

    def test_update_nonexistent_returns_false(self):
        mem = ImperiumMemory()
        assert mem.update_success_rate("x", "y", "z", 0.5) is False

    def test_get_stats(self):
        mem = ImperiumMemory()
        mem.store_memory("codebot", "patterns", "k1", {"a": 1})
        mem.store_memory("codebot", "fixes", "k2", {"b": 2})
        mem.store_memory("testbot", "coverage", "k3", {"c": 3})

        stats = mem.get_stats()
        assert stats["total_entries"] == 3
        assert stats["agents"]["codebot"]["total_entries"] == 2
        assert "patterns" in stats["agents"]["codebot"]["categories"]
        assert stats["agents"]["testbot"]["total_entries"] == 1

    def test_overwrite_same_key(self):
        mem = ImperiumMemory()
        mem.store_memory("bot", "cat", "key", {"v": 1})
        mem.store_memory("bot", "cat", "key", {"v": 2})
        result = mem.recall("bot", "cat", "key")
        assert result["v"] == 2


class TestMemoryPersistence:
    """Test disk save/load."""

    def test_save_and_load(self, temp_dir):
        path = os.path.join(temp_dir, "memory.json")

        # Save
        mem = ImperiumMemory(persistence_path=path)
        mem.store_memory("bot", "patterns", "key1", {"data": "hello"}, 0.88)
        assert os.path.exists(path)

        # Load in new instance
        mem2 = ImperiumMemory(persistence_path=path)
        result = mem2.recall("bot", "patterns", "key1")
        assert result is not None
        assert result["data"] == "hello"

    def test_load_nonexistent_path_no_crash(self):
        mem = ImperiumMemory(persistence_path="/tmp/nonexistent_imperium_test.json")
        assert mem.get_stats()["total_entries"] == 0

    def test_persistence_preserves_success_rate(self, temp_dir):
        path = os.path.join(temp_dir, "mem.json")
        mem = ImperiumMemory(persistence_path=path)
        mem.store_memory("bot", "cat", "key", {"x": 1}, success_rate=0.77)

        mem2 = ImperiumMemory(persistence_path=path)
        entry = mem2.store["bot"]["cat"]["key"]
        assert entry.success_rate == 0.77

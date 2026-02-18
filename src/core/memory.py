"""
Imperium Memory - Shared Knowledge Store for AI Agents.
Stores agent experiences, patterns, and learnings for continuous improvement.
Provides contextual memory retrieval to enhance future agent decisions.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class MemoryEntry:
    """A single memory entry stored by an agent."""
    agent_name: str
    category: str           # e.g., "refactoring_pattern", "bug_fix", "optimization"
    key: str                # Unique identifier within category
    value: Dict[str, Any]   # The actual knowledge
    success_rate: float = 1.0   # How effective this knowledge has been (0.0 - 1.0)
    access_count: int = 0       # How many times this has been accessed
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_name": self.agent_name,
            "category": self.category,
            "key": self.key,
            "value": self.value,
            "success_rate": self.success_rate,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }


class ImperiumMemory:
    """
    Shared Knowledge Store for Imperium Flow agents.
    
    Enables agents to:
    - Store successful patterns and strategies
    - Retrieve contextual knowledge for current tasks
    - Learn from past successes and failures
    - Share knowledge across agent types
    
    Memory is organized by agent → category → key.
    """

    def __init__(self, persistence_path: Optional[str] = None):
        self.logger = logging.getLogger("ImperiumMemory")
        self.store: Dict[str, Dict[str, Dict[str, MemoryEntry]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        self.persistence_path = persistence_path
        
        # Load from disk if path provided
        if persistence_path and os.path.exists(persistence_path):
            self._load_from_disk()

        self.logger.info("🧠 Imperium Memory initialized")

    def store_memory(
        self,
        agent_name: str,
        category: str,
        key: str,
        value: Dict[str, Any],
        success_rate: float = 1.0
    ) -> None:
        """
        Store a piece of knowledge.
        
        Example:
            memory.store_memory("codebot", "refactoring_pattern", "extract_method", {
                "pattern": "extract_method",
                "contexts": ["large_functions", "duplication"],
                "steps": ["identify", "extract", "test", "refactor"]
            }, success_rate=0.94)
        """
        entry = MemoryEntry(
            agent_name=agent_name,
            category=category,
            key=key,
            value=value,
            success_rate=success_rate
        )
        self.store[agent_name][category][key] = entry
        self.logger.info(
            f"💾 Stored: {agent_name}/{category}/{key} "
            f"(success_rate: {success_rate:.0%})"
        )

        if self.persistence_path:
            self._save_to_disk()

    def recall(
        self,
        agent_name: str,
        category: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Recall a specific memory entry.
        Updates access count and last_accessed timestamp.
        """
        entry = self.store.get(agent_name, {}).get(category, {}).get(key)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            self.logger.info(f"🔍 Recalled: {agent_name}/{category}/{key}")
            return entry.value
        return None

    def recall_by_category(
        self,
        agent_name: str,
        category: str,
        min_success_rate: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Recall all memories in a category, filtered by minimum success rate.
        Returns sorted by success_rate (highest first).
        """
        entries = self.store.get(agent_name, {}).get(category, {})
        results = [
            entry.to_dict()
            for entry in entries.values()
            if entry.success_rate >= min_success_rate
        ]
        results.sort(key=lambda x: x["success_rate"], reverse=True)
        return results

    def recall_cross_agent(
        self,
        category: str,
        min_success_rate: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Recall memories across ALL agents for a given category.
        Useful for sharing best practices between agents.
        """
        results = []
        for agent_name, categories in self.store.items():
            for key, entry in categories.get(category, {}).items():
                if entry.success_rate >= min_success_rate:
                    results.append(entry.to_dict())

        results.sort(key=lambda x: x["success_rate"], reverse=True)
        self.logger.info(
            f"🌐 Cross-agent recall for '{category}': "
            f"{len(results)} entries found"
        )
        return results

    def update_success_rate(
        self,
        agent_name: str,
        category: str,
        key: str,
        new_rate: float
    ) -> bool:
        """Update the success rate of a memory entry."""
        entry = self.store.get(agent_name, {}).get(category, {}).get(key)
        if entry:
            old_rate = entry.success_rate
            entry.success_rate = new_rate
            self.logger.info(
                f"📊 Updated success rate: {agent_name}/{category}/{key} "
                f"{old_rate:.0%} → {new_rate:.0%}"
            )
            if self.persistence_path:
                self._save_to_disk()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        total_entries = 0
        agent_stats = {}

        for agent_name, categories in self.store.items():
            agent_count = sum(len(entries) for entries in categories.values())
            total_entries += agent_count
            agent_stats[agent_name] = {
                "total_entries": agent_count,
                "categories": list(categories.keys())
            }

        return {
            "total_entries": total_entries,
            "agents": agent_stats
        }

    def _save_to_disk(self):
        """Persist memory to disk as JSON."""
        data = {}
        for agent, categories in self.store.items():
            data[agent] = {}
            for cat, entries in categories.items():
                data[agent][cat] = {
                    k: e.to_dict() for k, e in entries.items()
                }

        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with open(self.persistence_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _load_from_disk(self):
        """Load memory from disk."""
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
            
            for agent, categories in data.items():
                for cat, entries in categories.items():
                    for key, entry_data in entries.items():
                        self.store[agent][cat][key] = MemoryEntry(
                            agent_name=entry_data["agent_name"],
                            category=entry_data["category"],
                            key=entry_data["key"],
                            value=entry_data["value"],
                            success_rate=entry_data.get("success_rate", 1.0),
                            access_count=entry_data.get("access_count", 0)
                        )
            self.logger.info(f"📂 Loaded memory from {self.persistence_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load memory: {e}")

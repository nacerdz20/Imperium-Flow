"""
Tests for Imperium Protocol — MessageBus, Priority Queuing, Subscribers.
"""

import pytest
from datetime import datetime, timedelta
from src.core.protocol import (
    MessageBus,
    ImperiumMessage,
    AgentType,
    IntentType,
    Priority,
)


class TestImperiumMessage:
    """Test the ImperiumMessage dataclass."""

    def test_default_fields(self):
        msg = ImperiumMessage()
        assert msg.sender == AgentType.ORCHESTRATOR
        assert msg.receiver == AgentType.CODE_WORKER
        assert msg.intent == IntentType.NOTIFY
        assert msg.priority == Priority.MEDIUM
        assert isinstance(msg.message_id, str)
        assert len(msg.message_id) == 36  # UUID format

    def test_custom_fields(self):
        msg = ImperiumMessage(
            sender=AgentType.CODE_WORKER,
            receiver=AgentType.TEST_WORKER,
            intent=IntentType.DELEGATE,
            priority=Priority.HIGH,
            payload={"task": "write tests"},
        )
        assert msg.sender == AgentType.CODE_WORKER
        assert msg.receiver == AgentType.TEST_WORKER
        assert msg.payload["task"] == "write tests"

    def test_is_not_expired_fresh(self):
        msg = ImperiumMessage(ttl_seconds=3600)
        assert msg.is_expired() is False

    def test_is_expired_old(self):
        msg = ImperiumMessage(ttl_seconds=0)
        msg.timestamp = datetime.now() - timedelta(seconds=10)
        assert msg.is_expired() is True

    def test_to_dict_serialization(self):
        msg = ImperiumMessage(
            sender=AgentType.BOARD,
            receiver=AgentType.ORCHESTRATOR,
            intent=IntentType.REPORT,
            priority=Priority.CRITICAL,
            payload={"approved": True},
            correlation_id="corr-123",
        )
        d = msg.to_dict()
        assert d["sender"] == "board"
        assert d["receiver"] == "orchestrator"
        assert d["intent"] == "report"
        assert d["priority"] == 4
        assert d["payload"]["approved"] is True
        assert d["correlation_id"] == "corr-123"
        assert "timestamp" in d

    def test_correlation_id_links_messages(self):
        corr_id = "workflow-42"
        m1 = ImperiumMessage(intent=IntentType.REQUEST, correlation_id=corr_id)
        m2 = ImperiumMessage(intent=IntentType.ACKNOWLEDGE, correlation_id=corr_id)
        assert m1.correlation_id == m2.correlation_id


class TestMessageBus:
    """Test the MessageBus routing and queuing."""

    def test_send_returns_message_id(self):
        bus = MessageBus()
        msg = ImperiumMessage()
        mid = bus.send(msg)
        assert mid == msg.message_id

    def test_send_and_receive(self):
        bus = MessageBus()
        msg = ImperiumMessage(
            sender=AgentType.ORCHESTRATOR,
            receiver=AgentType.CODE_WORKER,
            payload={"action": "implement"},
        )
        bus.send(msg)
        received = bus.receive(AgentType.CODE_WORKER)
        assert received is not None
        assert received.payload["action"] == "implement"

    def test_receive_empty_queue_returns_none(self):
        bus = MessageBus()
        result = bus.receive(AgentType.CODE_WORKER)
        assert result is None

    def test_priority_ordering(self):
        bus = MessageBus()
        low = ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            priority=Priority.LOW,
            payload={"name": "low"},
        )
        high = ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            priority=Priority.HIGH,
            payload={"name": "high"},
        )
        bus.send(low)
        bus.send(high)
        first = bus.receive(AgentType.CODE_WORKER)
        assert first.payload["name"] == "high"
        second = bus.receive(AgentType.CODE_WORKER)
        assert second.payload["name"] == "low"

    def test_critical_bypasses_queue_and_triggers_callback(self):
        bus = MessageBus()
        received_messages = []

        def callback(msg):
            received_messages.append(msg)

        bus.subscribe(AgentType.CODE_WORKER, callback)
        critical = ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            priority=Priority.CRITICAL,
            payload={"alert": "production down"},
        )
        bus.send(critical)

        # CRITICAL goes to callback, not queue
        assert len(received_messages) == 1
        assert received_messages[0].payload["alert"] == "production down"
        # Queue should be empty
        assert bus.receive(AgentType.CODE_WORKER) is None

    def test_expired_messages_filtered_on_receive(self):
        bus = MessageBus()
        msg = ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            ttl_seconds=0,
        )
        msg.timestamp = datetime.now() - timedelta(seconds=10)
        bus.send(msg)
        result = bus.receive(AgentType.CODE_WORKER)
        assert result is None

    def test_queue_depth(self):
        bus = MessageBus()
        for i in range(5):
            bus.send(ImperiumMessage(
                receiver=AgentType.TEST_WORKER,
                payload={"i": i},
            ))
        assert bus.get_queue_depth(AgentType.TEST_WORKER) == 5
        assert bus.get_queue_depth(AgentType.CODE_WORKER) == 0

    def test_history_records_all_messages(self):
        bus = MessageBus()
        for _ in range(3):
            bus.send(ImperiumMessage())
        history = bus.get_history()
        assert len(history) == 3
        assert all("message_id" in h for h in history)

    def test_history_limit(self):
        bus = MessageBus()
        for _ in range(10):
            bus.send(ImperiumMessage())
        history = bus.get_history(limit=3)
        assert len(history) == 3

    def test_multiple_subscribers(self):
        bus = MessageBus()
        results = {"a": [], "b": []}
        bus.subscribe(AgentType.CODE_WORKER, lambda m: results["a"].append(m))
        bus.subscribe(AgentType.CODE_WORKER, lambda m: results["b"].append(m))
        bus.send(ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            priority=Priority.CRITICAL,
        ))
        assert len(results["a"]) == 1
        assert len(results["b"]) == 1

    def test_subscriber_error_does_not_crash(self):
        bus = MessageBus()

        def bad_callback(msg):
            raise ValueError("callback error")

        bus.subscribe(AgentType.CODE_WORKER, bad_callback)
        # Should not raise
        bus.send(ImperiumMessage(
            receiver=AgentType.CODE_WORKER,
            priority=Priority.CRITICAL,
        ))

    def test_messages_routed_to_correct_agent(self):
        bus = MessageBus()
        bus.send(ImperiumMessage(receiver=AgentType.CODE_WORKER))
        bus.send(ImperiumMessage(receiver=AgentType.TEST_WORKER))
        assert bus.get_queue_depth(AgentType.CODE_WORKER) == 1
        assert bus.get_queue_depth(AgentType.TEST_WORKER) == 1
        assert bus.get_queue_depth(AgentType.UI_WORKER) == 0

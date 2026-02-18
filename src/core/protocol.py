"""
Imperium Protocol - Inter-Agent Communication System.
Defines the standard message format for communication between agents,
including priority levels, intent types, and message routing.
"""

import logging
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


class AgentType(Enum):
    """Types of agents in the Imperium system."""
    CODE_WORKER = "code_worker"
    TEST_WORKER = "test_worker"
    UI_WORKER = "ui_worker"
    INTEGRATION_WORKER = "integration_worker"
    ORCHESTRATOR = "orchestrator"
    BOARD = "board"


class IntentType(Enum):
    """Intent of the message."""
    REQUEST = "request"         # Ask another agent to do something
    NOTIFY = "notify"           # Inform about a state change
    DELEGATE = "delegate"       # Hand off a task
    REPORT = "report"           # Report results
    ESCALATE = "escalate"       # Escalate to higher authority
    ACKNOWLEDGE = "acknowledge" # Confirm receipt


class Priority(Enum):
    """Message priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ImperiumMessage:
    """
    Standard message format for inter-agent communication.
    
    All communication between agents flows through ImperiumMessages,
    ensuring traceability, priority handling, and structured payloads.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: AgentType = AgentType.ORCHESTRATOR
    receiver: AgentType = AgentType.CODE_WORKER
    intent: IntentType = IntentType.NOTIFY
    priority: Priority = Priority.MEDIUM
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # Links related messages
    ttl_seconds: int = 3600  # Time to live (1 hour default)

    def is_expired(self) -> bool:
        """Check if message has expired."""
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed > self.ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "intent": self.intent.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "ttl_seconds": self.ttl_seconds
        }


class MessageBus:
    """
    Central message bus for the Imperium Protocol.
    
    Handles routing, priority queuing, and message history.
    CRITICAL priority messages bypass the queue and are processed immediately.
    """

    def __init__(self):
        self.logger = logging.getLogger("ImperiumProtocol")
        self.queues: Dict[AgentType, List[ImperiumMessage]] = defaultdict(list)
        self.history: List[ImperiumMessage] = []
        self.subscribers: Dict[AgentType, List[callable]] = defaultdict(list)
        self.logger.info("📡 Imperium Protocol MessageBus initialized")

    def send(self, message: ImperiumMessage) -> str:
        """
        Send a message to the target agent's queue.
        Returns the message_id for tracking.
        """
        self.history.append(message)

        # CRITICAL messages trigger immediate callback
        if message.priority == Priority.CRITICAL:
            self.logger.warning(
                f"🚨 CRITICAL message from {message.sender.value} "
                f"to {message.receiver.value}: {message.intent.value}"
            )
            self._notify_subscribers(message)
        else:
            # Insert sorted by priority (highest first)
            queue = self.queues[message.receiver]
            queue.append(message)
            queue.sort(key=lambda m: m.priority.value, reverse=True)

        self.logger.info(
            f"📤 [{message.priority.name}] {message.sender.value} → "
            f"{message.receiver.value}: {message.intent.value}"
        )
        return message.message_id

    def receive(self, agent: AgentType) -> Optional[ImperiumMessage]:
        """
        Receive the highest priority message for an agent.
        Returns None if queue is empty.
        """
        queue = self.queues.get(agent, [])
        # Filter expired messages
        queue[:] = [m for m in queue if not m.is_expired()]

        if not queue:
            return None

        message = queue.pop(0)
        self.logger.info(
            f"📥 {agent.value} received [{message.priority.name}]: "
            f"{message.intent.value} from {message.sender.value}"
        )
        return message

    def subscribe(self, agent: AgentType, callback: callable):
        """Subscribe to real-time message notifications."""
        self.subscribers[agent].append(callback)

    def _notify_subscribers(self, message: ImperiumMessage):
        """Notify all subscribers of the target agent."""
        for callback in self.subscribers.get(message.receiver, []):
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"Subscriber callback failed: {e}")

    def get_queue_depth(self, agent: AgentType) -> int:
        """Get the number of pending messages for an agent."""
        return len(self.queues.get(agent, []))

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent message history."""
        return [m.to_dict() for m in self.history[-limit:]]

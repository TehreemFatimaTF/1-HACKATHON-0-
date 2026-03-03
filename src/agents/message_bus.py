"""
Message Bus for Agent Communication (Platinum Tier)
Enables agents to communicate and coordinate tasks
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
import json
from pathlib import Path
import threading


class MessageBus:
    """
    Central message bus for agent-to-agent communication.
    Implements publish-subscribe pattern for loose coupling.
    """

    def __init__(self, log_dir: str = "Logs"):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[Dict] = []
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()

    def publish(self, topic: str, message: Dict, sender_id: str = None) -> bool:
        """
        Publish message to a topic

        Args:
            topic: Topic name (e.g., "task.completed", "agent.status")
            message: Message payload
            sender_id: ID of sending agent

        Returns:
            bool: True if message published successfully
        """
        try:
            with self.lock:
                # Add metadata
                full_message = {
                    "topic": topic,
                    "sender_id": sender_id,
                    "timestamp": datetime.now().isoformat(),
                    "payload": message
                }

                # Store in history
                self.message_history.append(full_message)

                # Notify subscribers
                if topic in self.subscribers:
                    for callback in self.subscribers[topic]:
                        try:
                            callback(full_message)
                        except Exception as e:
                            print(f"[MessageBus] Error in subscriber callback: {e}")

                # Log message
                self._log_message(full_message)

                return True

        except Exception as e:
            print(f"[MessageBus] Failed to publish message: {e}")
            return False

    def subscribe(self, topic: str, callback: Callable) -> bool:
        """
        Subscribe to a topic

        Args:
            topic: Topic name to subscribe to
            callback: Function to call when message received

        Returns:
            bool: True if subscribed successfully
        """
        try:
            with self.lock:
                if topic not in self.subscribers:
                    self.subscribers[topic] = []

                self.subscribers[topic].append(callback)
                print(f"[MessageBus] Subscribed to topic: {topic}")
                return True

        except Exception as e:
            print(f"[MessageBus] Failed to subscribe: {e}")
            return False

    def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """
        Unsubscribe from a topic

        Args:
            topic: Topic name
            callback: Callback function to remove

        Returns:
            bool: True if unsubscribed successfully
        """
        try:
            with self.lock:
                if topic in self.subscribers and callback in self.subscribers[topic]:
                    self.subscribers[topic].remove(callback)
                    return True
                return False

        except Exception as e:
            print(f"[MessageBus] Failed to unsubscribe: {e}")
            return False

    def route_task(self, task: Dict, target_agent_id: str) -> bool:
        """
        Route task to specific agent

        Args:
            task: Task to route
            target_agent_id: Target agent ID

        Returns:
            bool: True if routed successfully
        """
        return self.publish(
            topic=f"agent.{target_agent_id}.task",
            message=task,
            sender_id="orchestrator"
        )

    def broadcast(self, message: Dict, sender_id: str = None) -> bool:
        """
        Broadcast message to all agents

        Args:
            message: Message to broadcast
            sender_id: ID of sending agent

        Returns:
            bool: True if broadcast successfully
        """
        return self.publish(
            topic="broadcast.all",
            message=message,
            sender_id=sender_id
        )

    def get_message_history(
        self,
        topic: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get message history

        Args:
            topic: Filter by topic (optional)
            limit: Maximum number of messages to return

        Returns:
            List[Dict]: Message history
        """
        with self.lock:
            if topic:
                filtered = [m for m in self.message_history if m["topic"] == topic]
                return filtered[-limit:]
            else:
                return self.message_history[-limit:]

    def get_stats(self) -> Dict:
        """
        Get message bus statistics

        Returns:
            Dict: Statistics
        """
        with self.lock:
            return {
                "total_messages": len(self.message_history),
                "active_topics": len(self.subscribers),
                "topics": list(self.subscribers.keys()),
                "subscribers_per_topic": {
                    topic: len(callbacks)
                    for topic, callbacks in self.subscribers.items()
                }
            }

    def _log_message(self, message: Dict):
        """Log message to file"""
        try:
            log_file = self.log_dir / "message_bus.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message) + "\n")
        except Exception as e:
            print(f"[MessageBus] Failed to log message: {e}")

    def clear_history(self):
        """Clear message history (for testing)"""
        with self.lock:
            self.message_history.clear()

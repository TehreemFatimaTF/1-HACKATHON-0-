"""
Agent Orchestrator for Platinum Tier
Coordinates multiple agents and delegates tasks
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from .base_agent import BaseAgent, AgentStatus, AgentCapability
from .message_bus import MessageBus
from .email_agent import EmailAgent
from .social_media_agent import SocialMediaAgent
from .analytics_agent import AnalyticsAgent


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents.
    Handles task delegation, agent coordination, and result aggregation.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        self.message_bus = message_bus or MessageBus()
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.failed_tasks: List[Dict] = []

        # Initialize default agents
        self._initialize_default_agents()

        # Subscribe to agent events
        self._setup_subscriptions()

    def _initialize_default_agents(self):
        """Initialize default set of agents"""
        # Email Agent
        email_agent = EmailAgent()
        self.register_agent(email_agent)

        # Social Media Agent
        social_agent = SocialMediaAgent()
        self.register_agent(social_agent)

        # Analytics Agent
        analytics_agent = AnalyticsAgent()
        self.register_agent(analytics_agent)

        print(f"[Orchestrator] Initialized {len(self.agents)} agents")

    def _setup_subscriptions(self):
        """Setup message bus subscriptions"""
        self.message_bus.subscribe("task.completed", self._on_task_completed)
        self.message_bus.subscribe("task.failed", self._on_task_failed)
        self.message_bus.subscribe("agent.status", self._on_agent_status)

    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the orchestrator

        Args:
            agent: Agent to register

        Returns:
            bool: True if registered successfully
        """
        try:
            self.agents[agent.agent_id] = agent
            print(f"[Orchestrator] Registered agent: {agent.name} ({agent.agent_id[:8]}...)")
            return True
        except Exception as e:
            print(f"[Orchestrator] Failed to register agent: {e}")
            return False

    def delegate_task(self, task: Dict) -> Dict:
        """
        Delegate task to appropriate agent

        Args:
            task: Task to delegate

        Returns:
            Dict: Delegation result
        """
        try:
            # Find capable agent
            capable_agent = self._find_capable_agent(task)

            if not capable_agent:
                return {
                    "success": False,
                    "error": "No capable agent found for task",
                    "task_id": task.get("task_id")
                }

            # Add task to agent's queue
            if capable_agent.add_task(task):
                # Route task via message bus
                self.message_bus.route_task(task, capable_agent.agent_id)

                # Execute task
                result = capable_agent.execute_task(task)

                # Publish result
                if result.get("success"):
                    self.message_bus.publish(
                        "task.completed",
                        result,
                        sender_id=capable_agent.agent_id
                    )
                else:
                    self.message_bus.publish(
                        "task.failed",
                        result,
                        sender_id=capable_agent.agent_id
                    )

                return result
            else:
                return {
                    "success": False,
                    "error": "Agent rejected task",
                    "task_id": task.get("task_id")
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Task delegation failed: {str(e)}",
                "task_id": task.get("task_id")
            }

    def delegate_batch(self, tasks: List[Dict]) -> List[Dict]:
        """
        Delegate multiple tasks in batch

        Args:
            tasks: List of tasks to delegate

        Returns:
            List[Dict]: Results for each task
        """
        results = []
        for task in tasks:
            result = self.delegate_task(task)
            results.append(result)
        return results

    def _find_capable_agent(self, task: Dict) -> Optional[BaseAgent]:
        """
        Find agent capable of handling task

        Args:
            task: Task to handle

        Returns:
            Optional[BaseAgent]: Capable agent or None
        """
        # Find all capable agents
        capable_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle(task) and agent.status != AgentStatus.OFFLINE
        ]

        if not capable_agents:
            return None

        # Prefer idle agents
        idle_agents = [a for a in capable_agents if a.status == AgentStatus.IDLE]
        if idle_agents:
            # Return agent with lowest queue length
            return min(idle_agents, key=lambda a: len(a.task_queue))

        # Return any capable agent
        return capable_agents[0]

    def monitor_agents(self) -> Dict:
        """
        Monitor all agents and return status

        Returns:
            Dict: Agent monitoring data
        """
        agent_statuses = {}

        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()

        return {
            "total_agents": len(self.agents),
            "active_agents": sum(
                1 for a in self.agents.values()
                if a.status != AgentStatus.OFFLINE
            ),
            "agent_statuses": agent_statuses,
            "message_bus_stats": self.message_bus.get_stats()
        }

    def handle_failures(self) -> Dict:
        """
        Handle failed tasks and attempt recovery

        Returns:
            Dict: Recovery results
        """
        recovery_results = {
            "attempted": 0,
            "recovered": 0,
            "failed": 0
        }

        for failed_task in self.failed_tasks[:]:  # Copy list
            recovery_results["attempted"] += 1

            # Retry task
            result = self.delegate_task(failed_task)

            if result.get("success"):
                recovery_results["recovered"] += 1
                self.failed_tasks.remove(failed_task)
            else:
                recovery_results["failed"] += 1

        return recovery_results

    def aggregate_results(self, task_ids: List[str]) -> Dict:
        """
        Aggregate results from multiple tasks

        Args:
            task_ids: List of task IDs to aggregate

        Returns:
            Dict: Aggregated results
        """
        results = []

        for task_id in task_ids:
            # Find task in completed tasks
            task_result = next(
                (t for t in self.completed_tasks if t.get("task_id") == task_id),
                None
            )
            if task_result:
                results.append(task_result)

        return {
            "total_tasks": len(task_ids),
            "completed": len(results),
            "results": results
        }

    def get_agent_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """
        Get agents by capability

        Args:
            capability: Required capability

        Returns:
            List[BaseAgent]: Agents with capability
        """
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]

    def broadcast_to_agents(self, message: Dict) -> bool:
        """
        Broadcast message to all agents

        Args:
            message: Message to broadcast

        Returns:
            bool: True if broadcast successful
        """
        return self.message_bus.broadcast(message, sender_id="orchestrator")

    def _on_task_completed(self, message: Dict):
        """Handle task completion event"""
        self.completed_tasks.append(message["payload"])
        print(f"[Orchestrator] Task completed: {message['payload'].get('task_id')}")

    def _on_task_failed(self, message: Dict):
        """Handle task failure event"""
        self.failed_tasks.append(message["payload"])
        print(f"[Orchestrator] Task failed: {message['payload'].get('task_id')}")

    def _on_agent_status(self, message: Dict):
        """Handle agent status update"""
        print(f"[Orchestrator] Agent status update: {message['payload']}")

    def get_orchestrator_stats(self) -> Dict:
        """
        Get orchestrator statistics

        Returns:
            Dict: Orchestrator stats
        """
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(
                1 for a in self.agents.values()
                if a.status != AgentStatus.OFFLINE
            ),
            "tasks_in_queue": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "success_rate": (
                len(self.completed_tasks) /
                max(len(self.completed_tasks) + len(self.failed_tasks), 1) * 100
            ),
            "agents": {
                agent.name: {
                    "status": agent.status.value,
                    "tasks_completed": agent.metrics["tasks_completed"],
                    "success_rate": agent.metrics["success_rate"]
                }
                for agent in self.agents.values()
            }
        }

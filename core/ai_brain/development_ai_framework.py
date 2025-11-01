#!/usr/bin/env python3
"""
FixItFred Development AI Framework
Core orchestration system for AI-powered development enhancement
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from .ai_team_integration import FixItFredAITeam


class DevelopmentTaskType(Enum):
    """Types of development tasks that can be handled by AI agents"""

    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    DEPLOYMENT = "deployment"
    BUG_DETECTION = "bug_detection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ARCHITECTURE_DESIGN = "architecture_design"
    REFACTORING = "refactoring"
    INTEGRATION = "integration"


class AgentStatus(Enum):
    """Agent operational status"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class DevelopmentTask:
    """Represents a development task for AI agents"""

    task_id: str
    task_type: DevelopmentTaskType
    description: str
    context: Dict[str, Any]
    priority: int = 5  # 1-10, 10 being highest
    assigned_agents: List[str] = None
    status: str = "pending"
    created_at: datetime = None
    completed_at: datetime = None
    result: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.assigned_agents is None:
            self.assigned_agents = []


@dataclass
class AgentCapability:
    """Defines an agent's capabilities and specializations"""

    agent_id: str
    name: str
    specializations: List[DevelopmentTaskType]
    primary_ai_provider: str
    fallback_ai_provider: str
    confidence_threshold: float = 0.7
    max_concurrent_tasks: int = 3
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: List[str] = None

    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []


class DevelopmentContext:
    """Shared context for all development agents"""

    def __init__(self):
        self.project_state: Dict[str, Any] = {}
        self.code_repository: str = ""
        self.current_modules: List[str] = []
        self.active_deployments: List[str] = []
        self.performance_baselines: Dict[str, float] = {}
        self.quality_metrics: Dict[str, Any] = {}
        self.learning_history: List[Dict[str, Any]] = []
        self.task_history: List[DevelopmentTask] = []

    def update_project_state(self, key: str, value: Any):
        """Update project state with new information"""
        self.project_state[key] = value

    def add_learning_entry(self, task_type: str, outcome: str, lessons: Dict[str, Any]):
        """Add learning entry from completed tasks"""
        self.learning_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
                "outcome": outcome,
                "lessons": lessons,
            }
        )

    def get_relevant_context(self, task_type: DevelopmentTaskType) -> Dict[str, Any]:
        """Get context relevant to a specific task type"""
        return {
            "project_state": self.project_state,
            "modules": self.current_modules,
            "baselines": self.performance_baselines,
            "metrics": self.quality_metrics,
            "recent_lessons": [
                entry
                for entry in self.learning_history[-10:]
                if entry["task_type"] == task_type.value
            ],
        }


class DevelopmentEventBus:
    """Event-driven communication system for development agents"""

    def __init__(self):
        self.subscribers: Dict[str, List[str]] = {}  # event_type -> [agent_ids]
        self.event_history: List[Dict[str, Any]] = []

    async def publish_event(
        self, event_type: str, payload: Dict[str, Any], target_agents: List[str] = None
    ):
        """Publish development event to relevant agents"""
        event = {
            "event_id": f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
            "target_agents": target_agents or self.subscribers.get(event_type, []),
        }

        self.event_history.append(event)

        # In a real implementation, this would notify agents
        logging.info(
            f"Published event {event_type} to {len(event['target_agents'])} agents"
        )

        return event["event_id"]

    async def subscribe_agent(self, agent_id: str, event_types: List[str]):
        """Subscribe agent to specific event types"""
        for event_type in event_types:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            if agent_id not in self.subscribers[event_type]:
                self.subscribers[event_type].append(agent_id)

    async def unsubscribe_agent(self, agent_id: str, event_types: List[str] = None):
        """Unsubscribe agent from event types"""
        if event_types is None:
            # Unsubscribe from all events
            for event_type in self.subscribers:
                if agent_id in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(agent_id)
        else:
            for event_type in event_types:
                if (
                    event_type in self.subscribers
                    and agent_id in self.subscribers[event_type]
                ):
                    self.subscribers[event_type].remove(agent_id)


class TaskOrchestrator:
    """Intelligent task delegation and coordination system"""

    def __init__(self, ai_team: FixItFredAITeam, context: DevelopmentContext):
        self.ai_team = ai_team
        self.context = context
        self.agents: Dict[str, AgentCapability] = {}
        self.task_queue: List[DevelopmentTask] = []
        self.active_tasks: Dict[str, DevelopmentTask] = {}

    def register_agent(self, capability: AgentCapability):
        """Register a new development agent"""
        self.agents[capability.agent_id] = capability
        logging.info(f"Registered agent: {capability.name} ({capability.agent_id})")

    async def analyze_task_requirements(self, task: DevelopmentTask) -> List[str]:
        """Determine which agents are needed for a task"""
        suitable_agents = []

        for agent_id, agent in self.agents.items():
            if (
                task.task_type in agent.specializations
                and agent.status == AgentStatus.IDLE
                and len(agent.current_tasks) < agent.max_concurrent_tasks
            ):
                suitable_agents.append(agent_id)

        return suitable_agents

    async def delegate_to_best_agent(self, task: DevelopmentTask) -> Optional[str]:
        """Route task to most capable agent"""
        suitable_agents = await self.analyze_task_requirements(task)

        if not suitable_agents:
            return None

        # Select agent based on specialization match and current load
        best_agent_id = min(
            suitable_agents, key=lambda aid: len(self.agents[aid].current_tasks)
        )

        # Assign task
        agent = self.agents[best_agent_id]
        agent.current_tasks.append(task.task_id)
        agent.status = AgentStatus.BUSY
        task.assigned_agents = [best_agent_id]
        task.status = "assigned"

        self.active_tasks[task.task_id] = task

        logging.info(f"Assigned task {task.task_id} to agent {agent.name}")
        return best_agent_id

    async def coordinate_parallel_execution(
        self, subtasks: List[DevelopmentTask]
    ) -> Dict[str, Any]:
        """Manage parallel agent execution"""
        results = {}
        assignments = []

        # Assign all subtasks
        for subtask in subtasks:
            agent_id = await self.delegate_to_best_agent(subtask)
            if agent_id:
                assignments.append((subtask, agent_id))
            else:
                # Queue task for later
                self.task_queue.append(subtask)

        # Execute assigned tasks (in real implementation, this would be async)
        for subtask, agent_id in assignments:
            try:
                result = await self._execute_task_with_agent(subtask, agent_id)
                results[subtask.task_id] = result
            except Exception as e:
                logging.error(f"Task {subtask.task_id} failed: {e}")
                results[subtask.task_id] = {"error": str(e)}

        return results

    async def _execute_task_with_agent(
        self, task: DevelopmentTask, agent_id: str
    ) -> Dict[str, Any]:
        """Execute a specific task with the assigned agent"""
        agent = self.agents[agent_id]

        # Get relevant context for the task
        task_context = self.context.get_relevant_context(task.task_type)

        # Prepare prompt for AI
        prompt = self._build_agent_prompt(task, agent, task_context)

        try:
            # Use AI team to execute the task
            response = await self.ai_team.collaborate_on_task(
                task_description=prompt,
                task_type=task.task_type.value,
                preferred_provider=agent.primary_ai_provider,
            )

            # Update task status
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = response

            # Update agent status
            agent.current_tasks.remove(task.task_id)
            if not agent.current_tasks:
                agent.status = AgentStatus.IDLE

            # Add learning entry
            self.context.add_learning_entry(
                task_type=task.task_type.value,
                outcome="success",
                lessons={
                    "agent_used": agent_id,
                    "confidence": response.get("confidence", 0),
                },
            )

            return response

        except Exception as e:
            # Handle task failure
            task.status = "failed"
            task.result = {"error": str(e)}

            agent.current_tasks.remove(task.task_id)
            if not agent.current_tasks:
                agent.status = AgentStatus.IDLE

            self.context.add_learning_entry(
                task_type=task.task_type.value,
                outcome="failure",
                lessons={"agent_used": agent_id, "error": str(e)},
            )

            raise

    def _build_agent_prompt(
        self, task: DevelopmentTask, agent: AgentCapability, context: Dict[str, Any]
    ) -> str:
        """Build specialized prompt for agent based on task and context"""
        prompt = f"""
{agent.name} Development Agent Task

Task Type: {task.task_type.value}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Task Context:
{json.dumps(task.context, indent=2)}

Please provide:
1. Analysis of the task requirements
2. Step-by-step execution plan
3. Implementation details
4. Quality assurance measures
5. Expected outcomes

Focus on your specialization: {', '.join([spec.value for spec in agent.specializations])}
Use {agent.primary_ai_provider} capabilities for optimal results.
"""
        return prompt


class DevelopmentAIFramework:
    """Main orchestration system for AI-powered development enhancement"""

    def __init__(self, api_keys: Dict[str, str]):
        self.ai_team = FixItFredAITeam(api_keys)
        self.context = DevelopmentContext()
        self.event_bus = DevelopmentEventBus()
        self.orchestrator = TaskOrchestrator(self.ai_team, self.context)

        # Initialize default agents
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize the standard development agents"""
        agents = [
            AgentCapability(
                agent_id="code_gen",
                name="Code Generation Agent",
                specializations=[
                    DevelopmentTaskType.CODE_GENERATION,
                    DevelopmentTaskType.REFACTORING,
                ],
                primary_ai_provider="grok",
                fallback_ai_provider="claude",
            ),
            AgentCapability(
                agent_id="test_ops",
                name="Testing Agent",
                specializations=[DevelopmentTaskType.TESTING],
                primary_ai_provider="claude",
                fallback_ai_provider="openai",
            ),
            AgentCapability(
                agent_id="doc_gen",
                name="Documentation Agent",
                specializations=[DevelopmentTaskType.DOCUMENTATION],
                primary_ai_provider="claude",
                fallback_ai_provider="gemini",
            ),
            AgentCapability(
                agent_id="code_reviewer",
                name="Code Review Agent",
                specializations=[DevelopmentTaskType.CODE_REVIEW],
                primary_ai_provider="claude",
                fallback_ai_provider="grok",
            ),
            AgentCapability(
                agent_id="deployer",
                name="Deployment Agent",
                specializations=[DevelopmentTaskType.DEPLOYMENT],
                primary_ai_provider="openai",
                fallback_ai_provider="claude",
            ),
            AgentCapability(
                agent_id="bug_hunter",
                name="Bug Detection Agent",
                specializations=[DevelopmentTaskType.BUG_DETECTION],
                primary_ai_provider="grok",
                fallback_ai_provider="claude",
            ),
            AgentCapability(
                agent_id="optimizer",
                name="Performance Optimization Agent",
                specializations=[DevelopmentTaskType.PERFORMANCE_OPTIMIZATION],
                primary_ai_provider="grok",
                fallback_ai_provider="openai",
            ),
        ]

        for agent in agents:
            self.orchestrator.register_agent(agent)

    async def create_development_task(
        self,
        task_type: DevelopmentTaskType,
        description: str,
        context: Dict[str, Any] = None,
        priority: int = 5,
    ) -> DevelopmentTask:
        """Create a new development task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        task = DevelopmentTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            context=context or {},
            priority=priority,
        )

        # Publish task creation event
        await self.event_bus.publish_event(
            "task_created",
            {
                "task_id": task_id,
                "task_type": task_type.value,
                "description": description,
            },
        )

        return task

    async def execute_development_task(self, task: DevelopmentTask) -> Dict[str, Any]:
        """Execute a development task using the appropriate agent"""
        agent_id = await self.orchestrator.delegate_to_best_agent(task)

        if not agent_id:
            return {"error": "No suitable agent available for this task"}

        try:
            result = await self.orchestrator._execute_task_with_agent(task, agent_id)

            # Publish completion event
            await self.event_bus.publish_event(
                "task_completed",
                {"task_id": task.task_id, "agent_id": agent_id, "result": result},
            )

            return result

        except Exception as e:
            # Publish failure event
            await self.event_bus.publish_event(
                "task_failed",
                {"task_id": task.task_id, "agent_id": agent_id, "error": str(e)},
            )

            return {"error": str(e)}

    async def generate_code(
        self, description: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate code using the Code Generation Agent"""
        task = await self.create_development_task(
            DevelopmentTaskType.CODE_GENERATION, description, context, priority=7
        )

        return await self.execute_development_task(task)

    async def review_code(
        self, code: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Review code using the Code Review Agent"""
        review_context = {"code_to_review": code}
        if context:
            review_context.update(context)

        task = await self.create_development_task(
            DevelopmentTaskType.CODE_REVIEW,
            "Review the provided code for quality, security, and best practices",
            review_context,
            priority=8,
        )

        return await self.execute_development_task(task)

    async def generate_tests(
        self, code: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate tests using the Testing Agent"""
        test_context = {"code_to_test": code}
        if context:
            test_context.update(context)

        task = await self.create_development_task(
            DevelopmentTaskType.TESTING,
            "Generate comprehensive tests for the provided code",
            test_context,
            priority=6,
        )

        return await self.execute_development_task(task)

    async def optimize_performance(
        self, code: str, metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize performance using the Performance Optimization Agent"""
        opt_context = {"code_to_optimize": code, "current_metrics": metrics or {}}

        task = await self.create_development_task(
            DevelopmentTaskType.PERFORMANCE_OPTIMIZATION,
            "Analyze and optimize the provided code for better performance",
            opt_context,
            priority=5,
        )

        return await self.execute_development_task(task)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: {
                "name": agent.name,
                "status": agent.status.value,
                "current_tasks": len(agent.current_tasks),
                "max_tasks": agent.max_concurrent_tasks,
                "specializations": [spec.value for spec in agent.specializations],
            }
            for agent_id, agent in self.orchestrator.agents.items()
        }

    def get_development_metrics(self) -> Dict[str, Any]:
        """Get development productivity metrics"""
        completed_tasks = [
            task for task in self.context.task_history if task.status == "completed"
        ]
        failed_tasks = [
            task for task in self.context.task_history if task.status == "failed"
        ]

        return {
            "total_tasks": len(self.context.task_history),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(completed_tasks) / len(self.context.task_history)
            if self.context.task_history
            else 0,
            "active_agents": len(
                [
                    a
                    for a in self.orchestrator.agents.values()
                    if a.status == AgentStatus.BUSY
                ]
            ),
            "learning_entries": len(self.context.learning_history),
            "event_history": len(self.event_bus.event_history),
        }

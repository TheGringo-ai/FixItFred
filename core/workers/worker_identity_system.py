#!/usr/bin/env python3
"""
FixItFred Worker Identity & Agent System
Each worker gets their own AI agent, interface, and personalized experience
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import core components
from core.identity.ai_identity_core import ai_identity_core
from core.ai_brain.fine_tuning_engine import fine_tuning_engine

class WorkerRole(Enum):
    """Standard worker roles across all modules"""
    TECHNICIAN = "technician"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    SPECIALIST = "specialist"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    INSPECTOR = "inspector"
    ENGINEER = "engineer"
    ADMIN = "admin"

@dataclass
class WorkerProfile:
    """Individual worker identity and context"""
    worker_id: str
    name: str
    email: str
    role: WorkerRole
    department: str
    shift: str
    site: str
    
    # Skills and Certifications
    skills: List[str]
    certifications: List[Dict[str, Any]]
    experience_years: int
    specializations: List[str]
    
    # Performance Metrics
    tasks_completed: int = 0
    efficiency_score: float = 0.0
    quality_score: float = 0.0
    safety_score: float = 100.0
    
    # AI Agent Configuration
    ai_agent_id: str = None
    ai_personality: str = "professional"
    ai_expertise_level: str = "standard"
    preferred_language: str = "en"
    
    # Access and Permissions
    modules_access: List[str] = None
    equipment_authorized: List[str] = None
    data_access_level: str = "standard"
    
    # Preferences
    interface_theme: str = "default"
    notification_preferences: Dict[str, bool] = None
    voice_enabled: bool = True
    mobile_app: bool = True

@dataclass
class WorkerAIAgent:
    """Personal AI agent for each worker"""
    agent_id: str
    worker_id: str
    name: str  # Agent's name (e.g., "Fred", "Assistant", custom name)
    
    # AI Configuration
    base_model: str = "llama-3.2"
    fine_tuned_model: Optional[str] = None
    personality_traits: List[str] = None
    expertise_domains: List[str] = None
    
    # Context and Memory
    conversation_history: List[Dict[str, Any]] = None
    learned_preferences: Dict[str, Any] = None
    task_patterns: Dict[str, Any] = None
    
    # Capabilities
    can_execute_tasks: bool = True
    can_make_decisions: bool = False
    can_approve_work: bool = False
    can_access_sensitive_data: bool = False
    
    # Performance
    interactions_count: int = 0
    helpful_rating: float = 5.0
    accuracy_rate: float = 95.0
    response_time_ms: int = 500

class WorkerIdentitySystem:
    """Manages individual worker identities and their AI agents"""
    
    def __init__(self):
        self.workers: Dict[str, WorkerProfile] = {}
        self.ai_agents: Dict[str, WorkerAIAgent] = {}
        self.worker_sessions: Dict[str, Dict[str, Any]] = {}
        self.task_queues: Dict[str, List[Dict[str, Any]]] = {}
        
    async def create_worker(self, worker_data: Dict[str, Any]) -> WorkerProfile:
        """Create a new worker profile with personal AI agent"""
        
        # Create worker profile
        worker = WorkerProfile(
            worker_id=f"W-{uuid.uuid4().hex[:8]}",
            name=worker_data["name"],
            email=worker_data["email"],
            role=WorkerRole(worker_data["role"]),
            department=worker_data["department"],
            shift=worker_data.get("shift", "day"),
            site=worker_data.get("site", "main"),
            skills=worker_data.get("skills", []),
            certifications=worker_data.get("certifications", []),
            experience_years=worker_data.get("experience_years", 0),
            specializations=worker_data.get("specializations", []),
            modules_access=worker_data.get("modules_access", []),
            equipment_authorized=worker_data.get("equipment_authorized", []),
            preferred_language=worker_data.get("preferred_language", "en")
        )
        
        # Create personal AI agent
        ai_agent = await self._create_personal_ai_agent(worker)
        worker.ai_agent_id = ai_agent.agent_id
        
        # Store worker and agent
        self.workers[worker.worker_id] = worker
        self.ai_agents[ai_agent.agent_id] = ai_agent
        
        # Initialize task queue
        self.task_queues[worker.worker_id] = []
        
        # Register with AI Identity Core
        await self._register_worker_identity(worker)
        
        return worker
    
    async def _create_personal_ai_agent(self, worker: WorkerProfile) -> WorkerAIAgent:
        """Create a personalized AI agent for the worker"""
        
        # Determine agent configuration based on role
        agent_config = self._get_agent_config_for_role(worker.role)
        
        # Create AI agent
        agent = WorkerAIAgent(
            agent_id=f"AI-{uuid.uuid4().hex[:8]}",
            worker_id=worker.worker_id,
            name=f"Fred-{worker.name.split()[0]}",  # Personalized agent name
            base_model="llama-3.2",
            personality_traits=agent_config["personality_traits"],
            expertise_domains=agent_config["expertise_domains"],
            conversation_history=[],
            learned_preferences={},
            task_patterns={},
            can_execute_tasks=agent_config["can_execute_tasks"],
            can_make_decisions=agent_config["can_make_decisions"],
            can_approve_work=agent_config["can_approve_work"],
            can_access_sensitive_data=agent_config["can_access_sensitive_data"]
        )
        
        # Fine-tune for specific role and department
        if worker.department in ["maintenance", "quality", "safety"]:
            agent.fine_tuned_model = await self._fine_tune_for_department(
                agent, worker.department, worker.specializations
            )
        
        return agent
    
    def _get_agent_config_for_role(self, role: WorkerRole) -> Dict[str, Any]:
        """Get AI agent configuration based on worker role"""
        
        configs = {
            WorkerRole.TECHNICIAN: {
                "personality_traits": ["helpful", "technical", "detail-oriented"],
                "expertise_domains": ["equipment", "troubleshooting", "maintenance"],
                "can_execute_tasks": True,
                "can_make_decisions": False,
                "can_approve_work": False,
                "can_access_sensitive_data": False
            },
            WorkerRole.OPERATOR: {
                "personality_traits": ["efficient", "safety-focused", "responsive"],
                "expertise_domains": ["operations", "procedures", "quality"],
                "can_execute_tasks": True,
                "can_make_decisions": False,
                "can_approve_work": False,
                "can_access_sensitive_data": False
            },
            WorkerRole.SUPERVISOR: {
                "personality_traits": ["leadership", "analytical", "supportive"],
                "expertise_domains": ["scheduling", "team-management", "optimization"],
                "can_execute_tasks": True,
                "can_make_decisions": True,
                "can_approve_work": True,
                "can_access_sensitive_data": False
            },
            WorkerRole.MANAGER: {
                "personality_traits": ["strategic", "analytical", "decisive"],
                "expertise_domains": ["planning", "analytics", "compliance", "budgeting"],
                "can_execute_tasks": True,
                "can_make_decisions": True,
                "can_approve_work": True,
                "can_access_sensitive_data": True
            },
            WorkerRole.SPECIALIST: {
                "personality_traits": ["expert", "innovative", "thorough"],
                "expertise_domains": ["specialized-knowledge", "problem-solving", "training"],
                "can_execute_tasks": True,
                "can_make_decisions": True,
                "can_approve_work": False,
                "can_access_sensitive_data": False
            },
            WorkerRole.ANALYST: {
                "personality_traits": ["analytical", "data-driven", "precise"],
                "expertise_domains": ["data-analysis", "reporting", "optimization"],
                "can_execute_tasks": True,
                "can_make_decisions": False,
                "can_approve_work": False,
                "can_access_sensitive_data": True
            },
            WorkerRole.COORDINATOR: {
                "personality_traits": ["organized", "communicative", "proactive"],
                "expertise_domains": ["coordination", "scheduling", "communication"],
                "can_execute_tasks": True,
                "can_make_decisions": False,
                "can_approve_work": False,
                "can_access_sensitive_data": False
            },
            WorkerRole.INSPECTOR: {
                "personality_traits": ["meticulous", "knowledgeable", "objective"],
                "expertise_domains": ["quality", "compliance", "standards", "auditing"],
                "can_execute_tasks": True,
                "can_make_decisions": True,
                "can_approve_work": True,
                "can_access_sensitive_data": False
            },
            WorkerRole.ENGINEER: {
                "personality_traits": ["innovative", "technical", "problem-solver"],
                "expertise_domains": ["design", "optimization", "technical-analysis"],
                "can_execute_tasks": True,
                "can_make_decisions": True,
                "can_approve_work": True,
                "can_access_sensitive_data": True
            },
            WorkerRole.ADMIN: {
                "personality_traits": ["supportive", "organized", "resourceful"],
                "expertise_domains": ["administration", "documentation", "coordination"],
                "can_execute_tasks": True,
                "can_make_decisions": False,
                "can_approve_work": False,
                "can_access_sensitive_data": True
            }
        }
        
        return configs.get(role, configs[WorkerRole.OPERATOR])
    
    async def _fine_tune_for_department(self, agent: WorkerAIAgent, 
                                       department: str, 
                                       specializations: List[str]) -> str:
        """Fine-tune AI agent for specific department and specializations"""
        
        # Create training data based on department
        training_context = {
            "department": department,
            "specializations": specializations,
            "industry_knowledge": True,
            "safety_protocols": True,
            "equipment_specific": True
        }
        
        # Use the fine-tuning engine
        fine_tuned_model_id = f"ft-{agent.agent_id}-{department}"
        
        # In production, this would actually fine-tune the model
        # For now, we're registering the configuration
        agent.expertise_domains.extend([
            f"{department}-expert",
            f"{department}-procedures",
            f"{department}-troubleshooting"
        ])
        
        return fine_tuned_model_id
    
    async def _register_worker_identity(self, worker: WorkerProfile):
        """Register worker with AI Identity Core for authentication"""
        
        # Create user claims for identity system
        from core.identity.ai_identity_core import UserClaims
        
        user_claims = UserClaims(
            user_id=worker.worker_id,
            tenant="default",  # Would be company-specific
            name=worker.name,
            email=worker.email,
            roles=[worker.role.value],
            department=worker.department,
            site=worker.site,
            shift=worker.shift,
            security_level="standard" if worker.role != WorkerRole.MANAGER else "elevated"
        )
        
        # Store in identity core
        ai_identity_core.user_contexts[worker.worker_id] = user_claims
    
    async def get_worker_dashboard(self, worker_id: str) -> Dict[str, Any]:
        """Get personalized dashboard for worker"""
        
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker {worker_id} not found")
        
        agent = self.ai_agents.get(worker.ai_agent_id)
        tasks = self.task_queues.get(worker_id, [])
        
        # Build personalized dashboard based on role
        dashboard = {
            "worker": {
                "name": worker.name,
                "role": worker.role.value,
                "department": worker.department,
                "shift": worker.shift
            },
            "ai_assistant": {
                "name": agent.name,
                "greeting": f"Hello {worker.name.split()[0]}! I'm {agent.name}, your AI assistant.",
                "capabilities": agent.expertise_domains,
                "personality": agent.personality_traits
            },
            "metrics": {
                "tasks_completed": worker.tasks_completed,
                "efficiency": worker.efficiency_score,
                "quality": worker.quality_score,
                "safety": worker.safety_score
            },
            "task_queue": tasks[:10],  # Next 10 tasks
            "quick_actions": self._get_quick_actions_for_role(worker.role),
            "modules_access": worker.modules_access,
            "notifications": [],
            "theme": worker.interface_theme
        }
        
        return dashboard
    
    def _get_quick_actions_for_role(self, role: WorkerRole) -> List[Dict[str, str]]:
        """Get role-specific quick actions"""
        
        actions = {
            WorkerRole.TECHNICIAN: [
                {"label": "Create Work Order", "action": "create_work_order", "icon": "wrench"},
                {"label": "View Equipment", "action": "view_equipment", "icon": "cog"},
                {"label": "Report Issue", "action": "report_issue", "icon": "alert-triangle"},
                {"label": "Check Schedule", "action": "check_schedule", "icon": "calendar"}
            ],
            WorkerRole.OPERATOR: [
                {"label": "Start Production", "action": "start_production", "icon": "play"},
                {"label": "Log Metrics", "action": "log_metrics", "icon": "chart"},
                {"label": "Quality Check", "action": "quality_check", "icon": "check-circle"},
                {"label": "View SOPs", "action": "view_procedures", "icon": "book"}
            ],
            WorkerRole.SUPERVISOR: [
                {"label": "Team Overview", "action": "team_overview", "icon": "users"},
                {"label": "Approve Work", "action": "approve_work", "icon": "check"},
                {"label": "Schedule Tasks", "action": "schedule_tasks", "icon": "clock"},
                {"label": "View Reports", "action": "view_reports", "icon": "file-text"}
            ],
            WorkerRole.MANAGER: [
                {"label": "Dashboard", "action": "executive_dashboard", "icon": "dashboard"},
                {"label": "Analytics", "action": "analytics", "icon": "trending-up"},
                {"label": "Approvals", "action": "pending_approvals", "icon": "check-square"},
                {"label": "Reports", "action": "generate_reports", "icon": "bar-chart"}
            ]
        }
        
        return actions.get(role, actions[WorkerRole.OPERATOR])
    
    async def process_worker_request(self, worker_id: str, 
                                    request: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Process request from worker through their personal AI agent"""
        
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker {worker_id} not found")
        
        agent = self.ai_agents.get(worker.ai_agent_id)
        
        # AI agent processes the request with worker context
        response = await self._ai_process_request(agent, worker, request, context)
        
        # Update agent learning
        agent.interactions_count += 1
        agent.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "response": response,
            "context": context
        })
        
        # Learn from interaction
        await self._update_agent_learning(agent, request, response)
        
        return response
    
    async def _ai_process_request(self, agent: WorkerAIAgent, 
                                 worker: WorkerProfile,
                                 request: str, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent processes worker request with full context"""
        
        # Build comprehensive context
        full_context = {
            "worker_role": worker.role.value,
            "department": worker.department,
            "shift": worker.shift,
            "site": worker.site,
            "skills": worker.skills,
            "agent_capabilities": agent.expertise_domains,
            "can_execute": agent.can_execute_tasks,
            "can_decide": agent.can_make_decisions,
            **context
        }
        
        # Determine request type and process accordingly
        request_lower = request.lower()
        
        if "help" in request_lower:
            return await self._provide_contextual_help(agent, worker, request)
        elif "task" in request_lower or "work" in request_lower:
            return await self._handle_task_request(agent, worker, request)
        elif "status" in request_lower or "report" in request_lower:
            return await self._provide_status_report(agent, worker, request)
        elif "approve" in request_lower and agent.can_approve_work:
            return await self._handle_approval_request(agent, worker, request)
        else:
            return await self._general_ai_response(agent, worker, request, full_context)
    
    async def _provide_contextual_help(self, agent: WorkerAIAgent, 
                                      worker: WorkerProfile, 
                                      request: str) -> Dict[str, Any]:
        """Provide role-specific help"""
        
        return {
            "type": "help",
            "response": f"Hi {worker.name.split()[0]}, I'm {agent.name}. I can help you with:\n" +
                       f"• {', '.join(agent.expertise_domains)}\n" +
                       f"• Your current tasks and schedule\n" +
                       f"• {worker.department} procedures and protocols\n" +
                       "What would you like assistance with?",
            "suggestions": self._get_quick_actions_for_role(worker.role)
        }
    
    async def _handle_task_request(self, agent: WorkerAIAgent, 
                                  worker: WorkerProfile, 
                                  request: str) -> Dict[str, Any]:
        """Handle task-related requests"""
        
        tasks = self.task_queues.get(worker.worker_id, [])
        
        return {
            "type": "task_response",
            "response": f"You have {len(tasks)} tasks in your queue.",
            "tasks": tasks[:5],  # Show next 5 tasks
            "can_execute": agent.can_execute_tasks,
            "actions": ["view_all", "start_task", "complete_task"]
        }
    
    async def _provide_status_report(self, agent: WorkerAIAgent, 
                                    worker: WorkerProfile, 
                                    request: str) -> Dict[str, Any]:
        """Provide status report"""
        
        return {
            "type": "status_report",
            "response": f"Here's your current status, {worker.name.split()[0]}:",
            "metrics": {
                "tasks_completed_today": worker.tasks_completed,
                "efficiency": f"{worker.efficiency_score}%",
                "quality": f"{worker.quality_score}%",
                "safety": f"{worker.safety_score}%"
            },
            "department_status": f"{worker.department} is operating normally",
            "shift_info": f"You're on {worker.shift} shift"
        }
    
    async def _handle_approval_request(self, agent: WorkerAIAgent, 
                                      worker: WorkerProfile, 
                                      request: str) -> Dict[str, Any]:
        """Handle approval requests for authorized workers"""
        
        if not agent.can_approve_work:
            return {
                "type": "error",
                "response": "You don't have approval authority for this action.",
                "suggestion": "Please contact your supervisor for approval."
            }
        
        return {
            "type": "approval",
            "response": "I can help you with approvals. What would you like to approve?",
            "pending_approvals": [],  # Would fetch actual pending items
            "actions": ["approve", "reject", "request_info"]
        }
    
    async def _general_ai_response(self, agent: WorkerAIAgent, 
                                  worker: WorkerProfile, 
                                  request: str,
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general AI response using agent's expertise"""
        
        # This would use the actual AI model (Llama, GPT, etc.)
        # For now, returning a structured response
        
        return {
            "type": "ai_response",
            "response": f"I understand you need help with: {request}. " +
                       f"Based on your role as {worker.role.value} in {worker.department}, " +
                       f"I recommend checking your task queue or consulting the procedures manual.",
            "agent": agent.name,
            "confidence": 0.85,
            "suggestions": self._get_quick_actions_for_role(worker.role)
        }
    
    async def _update_agent_learning(self, agent: WorkerAIAgent, 
                                    request: str, 
                                    response: Dict[str, Any]):
        """Update agent's learning from interaction"""
        
        # Track patterns
        if "task_patterns" not in agent.__dict__:
            agent.task_patterns = {}
        
        # Simple pattern tracking (would be ML in production)
        words = request.lower().split()
        for word in words:
            if word in agent.task_patterns:
                agent.task_patterns[word] += 1
            else:
                agent.task_patterns[word] = 1
        
        # Update preferences based on successful interactions
        if response.get("type") == "task_response":
            agent.learned_preferences["prefers_task_view"] = True
        elif response.get("type") == "status_report":
            agent.learned_preferences["checks_status_frequently"] = True
    
    async def assign_task_to_worker(self, worker_id: str, task: Dict[str, Any]):
        """Assign a task to a worker's queue"""
        
        if worker_id not in self.task_queues:
            self.task_queues[worker_id] = []
        
        task["assigned_at"] = datetime.now().isoformat()
        task["status"] = "pending"
        task["worker_id"] = worker_id
        
        self.task_queues[worker_id].append(task)
        
        # Notify worker's AI agent
        if worker_id in self.workers:
            agent_id = self.workers[worker_id].ai_agent_id
            if agent_id in self.ai_agents:
                # Agent would send notification to worker
                pass
    
    async def get_team_overview(self, supervisor_id: str) -> Dict[str, Any]:
        """Get team overview for supervisors/managers"""
        
        supervisor = self.workers.get(supervisor_id)
        if not supervisor or supervisor.role not in [WorkerRole.SUPERVISOR, WorkerRole.MANAGER]:
            raise ValueError("Unauthorized for team overview")
        
        # Get team members in same department
        team_members = [
            w for w in self.workers.values() 
            if w.department == supervisor.department and w.worker_id != supervisor_id
        ]
        
        team_overview = {
            "department": supervisor.department,
            "team_size": len(team_members),
            "members": [
                {
                    "name": member.name,
                    "role": member.role.value,
                    "status": "active",  # Would check actual status
                    "tasks_assigned": len(self.task_queues.get(member.worker_id, [])),
                    "efficiency": member.efficiency_score,
                    "ai_agent": self.ai_agents[member.ai_agent_id].name
                }
                for member in team_members
            ],
            "department_metrics": {
                "total_tasks": sum(len(self.task_queues.get(m.worker_id, [])) for m in team_members),
                "avg_efficiency": sum(m.efficiency_score for m in team_members) / len(team_members) if team_members else 0,
                "avg_quality": sum(m.quality_score for m in team_members) / len(team_members) if team_members else 0
            }
        }
        
        return team_overview

# Global worker identity system instance
worker_identity_system = WorkerIdentitySystem()

# Demo function
async def demo_worker_system():
    """Demo the worker identity system"""
    
    print("🎯 WORKER IDENTITY & AI AGENT SYSTEM DEMO")
    print("="*50)
    
    # Create different types of workers
    technician = await worker_identity_system.create_worker({
        "name": "John Smith",
        "email": "john.smith@company.com",
        "role": "technician",
        "department": "maintenance",
        "shift": "day",
        "site": "factory-1",
        "skills": ["electrical", "hydraulics", "plc"],
        "certifications": [{"name": "Electrical Safety", "expires": "2025-12-31"}],
        "experience_years": 5,
        "specializations": ["conveyor systems", "packaging equipment"],
        "modules_access": ["chatterfix", "safety"],
        "equipment_authorized": ["conveyor-1", "packaging-line-a"]
    })
    
    print(f"✅ Created Technician: {technician.name} (ID: {technician.worker_id})")
    print(f"   AI Agent: {worker_identity_system.ai_agents[technician.ai_agent_id].name}")
    
    supervisor = await worker_identity_system.create_worker({
        "name": "Sarah Johnson",
        "email": "sarah.johnson@company.com",
        "role": "supervisor",
        "department": "maintenance",
        "shift": "day",
        "site": "factory-1",
        "skills": ["leadership", "planning", "problem-solving"],
        "experience_years": 10,
        "modules_access": ["chatterfix", "safety", "quality", "operations"]
    })
    
    print(f"✅ Created Supervisor: {supervisor.name} (ID: {supervisor.worker_id})")
    print(f"   AI Agent: {worker_identity_system.ai_agents[supervisor.ai_agent_id].name}")
    
    # Get technician's dashboard
    dashboard = await worker_identity_system.get_worker_dashboard(technician.worker_id)
    print(f"\n📊 {technician.name}'s Dashboard:")
    print(f"   AI Assistant: {dashboard['ai_assistant']['greeting']}")
    print(f"   Quick Actions: {[a['label'] for a in dashboard['quick_actions']]}")
    
    # Process a request through AI agent
    response = await worker_identity_system.process_worker_request(
        technician.worker_id,
        "What tasks do I have today?",
        {"location": "packaging-area"}
    )
    print(f"\n🤖 AI Response: {response['response']}")
    
    # Assign a task
    await worker_identity_system.assign_task_to_worker(technician.worker_id, {
        "task_id": "T-001",
        "title": "Inspect Conveyor Belt",
        "priority": "high",
        "equipment": "conveyor-1",
        "estimated_time": "30 minutes"
    })
    print(f"\n📋 Task assigned to {technician.name}")
    
    # Get supervisor's team overview
    team = await worker_identity_system.get_team_overview(supervisor.worker_id)
    print(f"\n👥 {supervisor.name}'s Team Overview:")
    print(f"   Department: {team['department']}")
    print(f"   Team Size: {team['team_size']}")
    
    return {
        "technician": technician,
        "supervisor": supervisor,
        "ai_agents": [
            worker_identity_system.ai_agents[technician.ai_agent_id],
            worker_identity_system.ai_agents[supervisor.ai_agent_id]
        ]
    }

if __name__ == "__main__":
    asyncio.run(demo_worker_system())
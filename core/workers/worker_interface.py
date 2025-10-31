#!/usr/bin/env python3
"""
FixItFred Worker Interface System
Each module creates worker-specific interfaces where workers control AI agents
for daily tasks, data collection, and operational assistance
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class WorkerAgent:
    """AI agent assigned to a specific worker"""
    id: str
    worker_id: str
    module_type: str  # quality, maintenance, safety, operations, finance, hr
    name: str
    role: str  # inspector, technician, supervisor, operator, analyst
    capabilities: List[str]
    current_tasks: List[str]
    ai_personality: Dict[str, Any]
    status: str = 'active'  # active, busy, offline
    last_interaction: datetime = None
    
    def __post_init__(self):
        if self.last_interaction is None:
            self.last_interaction = datetime.now()

@dataclass
class WorkerTask:
    """Daily task for worker with AI assistance"""
    id: str
    worker_id: str
    agent_id: str
    title: str
    description: str
    task_type: str  # inspection, maintenance, data_entry, analysis, reporting
    priority: str = 'medium'  # low, medium, high, urgent
    status: str = 'pending'  # pending, in_progress, completed, needs_review
    ai_guidance: str = ''
    data_collected: Dict[str, Any] = None
    due_date: datetime = None
    created_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.data_collected is None:
            self.data_collected = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WorkerInterface:
    """Worker-specific interface for controlling AI agents and tasks"""
    worker_id: str
    name: str
    role: str
    department: str
    module_access: List[str]  # Which modules this worker can access
    assigned_agents: List[WorkerAgent]
    active_tasks: List[WorkerTask]
    permissions: List[str]
    shift_schedule: Dict[str, Any]
    preferences: Dict[str, Any]
    
    def __post_init__(self):
        if not hasattr(self, 'assigned_agents') or self.assigned_agents is None:
            self.assigned_agents = []
        if not hasattr(self, 'active_tasks') or self.active_tasks is None:
            self.active_tasks = []
        if not hasattr(self, 'permissions') or self.permissions is None:
            self.permissions = []
        if not hasattr(self, 'preferences') or self.preferences is None:
            self.preferences = {}

class WorkerInterfaceManager:
    """Manages worker interfaces and AI agent assignments"""
    
    def __init__(self):
        self.worker_interfaces: Dict[str, WorkerInterface] = {}
        self.worker_agents: Dict[str, WorkerAgent] = {}
        self.active_tasks: Dict[str, WorkerTask] = {}
        
        # Module-specific agent templates
        self.agent_templates = {
            'quality': {
                'Quality Inspector': {
                    'capabilities': [
                        'Visual inspection guidance',
                        'Defect pattern recognition',
                        'Quality data collection',
                        'Inspection report generation',
                        'Non-conformance reporting',
                        'Corrective action tracking'
                    ],
                    'ai_personality': {
                        'name': 'QualityBot',
                        'tone': 'precise',
                        'expertise': 'quality_control'
                    }
                },
                'Quality Technician': {
                    'capabilities': [
                        'Test procedure guidance',
                        'Measurement validation',
                        'Statistical analysis',
                        'Equipment calibration',
                        'Process monitoring',
                        'Data trend analysis'
                    ],
                    'ai_personality': {
                        'name': 'TestAssist',
                        'tone': 'technical',
                        'expertise': 'testing'
                    }
                }
            },
            'maintenance': {
                'Maintenance Technician': {
                    'capabilities': [
                        'Troubleshooting assistance',
                        'Repair procedure guidance',
                        'Parts identification',
                        'Preventive maintenance scheduling',
                        'Work order management',
                        'Equipment history tracking'
                    ],
                    'ai_personality': {
                        'name': 'MaintenanceAI',
                        'tone': 'practical',
                        'expertise': 'mechanical'
                    }
                },
                'Maintenance Supervisor': {
                    'capabilities': [
                        'Resource planning',
                        'Team coordination',
                        'Priority assessment',
                        'Performance monitoring',
                        'Budget tracking',
                        'Vendor coordination'
                    ],
                    'ai_personality': {
                        'name': 'PlannerBot',
                        'tone': 'managerial',
                        'expertise': 'planning'
                    }
                }
            },
            'safety': {
                'Safety Officer': {
                    'capabilities': [
                        'Hazard identification',
                        'Risk assessment',
                        'Incident investigation',
                        'Compliance monitoring',
                        'Training coordination',
                        'Emergency response'
                    ],
                    'ai_personality': {
                        'name': 'SafetyGuard',
                        'tone': 'cautious',
                        'expertise': 'safety'
                    }
                },
                'Safety Inspector': {
                    'capabilities': [
                        'Safety audit guidance',
                        'PPE verification',
                        'Environmental monitoring',
                        'Procedure compliance',
                        'Documentation assistance',
                        'Corrective action tracking'
                    ],
                    'ai_personality': {
                        'name': 'InspectBot',
                        'tone': 'thorough',
                        'expertise': 'inspection'
                    }
                }
            },
            'operations': {
                'Production Operator': {
                    'capabilities': [
                        'Process optimization',
                        'Production monitoring',
                        'Efficiency tracking',
                        'Quality checks',
                        'Equipment operation',
                        'Shift reporting'
                    ],
                    'ai_personality': {
                        'name': 'ProdAssist',
                        'tone': 'efficient',
                        'expertise': 'production'
                    }
                },
                'Operations Supervisor': {
                    'capabilities': [
                        'Team management',
                        'Production planning',
                        'Performance analysis',
                        'Resource coordination',
                        'Issue resolution',
                        'Reporting'
                    ],
                    'ai_personality': {
                        'name': 'OpsManager',
                        'tone': 'directive',
                        'expertise': 'operations'
                    }
                }
            }
        }
    
    async def create_worker_interface(self, worker_config: Dict[str, Any]) -> WorkerInterface:
        """Create a new worker interface with appropriate AI agents"""
        
        worker_id = worker_config.get('id', f"worker_{uuid.uuid4().hex[:8]}")
        
        # Create worker interface
        interface = WorkerInterface(
            worker_id=worker_id,
            name=worker_config['name'],
            role=worker_config['role'],
            department=worker_config['department'],
            module_access=worker_config.get('module_access', []),
            assigned_agents=[],
            active_tasks=[],
            permissions=worker_config.get('permissions', []),
            shift_schedule=worker_config.get('shift_schedule', {}),
            preferences=worker_config.get('preferences', {})
        )
        
        # Assign appropriate AI agents based on role and modules
        for module in interface.module_access:
            await self._assign_agent_to_worker(interface, module)
        
        self.worker_interfaces[worker_id] = interface
        return interface
    
    async def _assign_agent_to_worker(self, interface: WorkerInterface, module_type: str):
        """Assign an AI agent to a worker based on their role and module"""
        
        if module_type not in self.agent_templates:
            return
        
        # Find best matching agent template for worker's role
        agent_template = None
        for template_role, template_config in self.agent_templates[module_type].items():
            if interface.role.lower() in template_role.lower() or template_role.lower() in interface.role.lower():
                agent_template = template_config
                break
        
        # Default to first available if no exact match
        if not agent_template:
            agent_template = list(self.agent_templates[module_type].values())[0]
        
        # Create worker agent
        agent = WorkerAgent(
            id=f"{interface.worker_id}_{module_type}_agent",
            worker_id=interface.worker_id,
            module_type=module_type,
            name=agent_template['ai_personality']['name'],
            role=interface.role,
            capabilities=agent_template['capabilities'],
            current_tasks=[],
            ai_personality=agent_template['ai_personality']
        )
        
        interface.assigned_agents.append(agent)
        self.worker_agents[agent.id] = agent
    
    async def create_daily_tasks(self, worker_id: str, module_type: str) -> List[WorkerTask]:
        """Generate daily tasks for a worker with AI assistance"""
        
        if worker_id not in self.worker_interfaces:
            return []
        
        interface = self.worker_interfaces[worker_id]
        
        # Find appropriate agent for this module
        agent = None
        for assigned_agent in interface.assigned_agents:
            if assigned_agent.module_type == module_type:
                agent = assigned_agent
                break
        
        if not agent:
            return []
        
        # Generate module-specific tasks
        tasks = []
        task_templates = self._get_task_templates(module_type, interface.role)
        
        for task_template in task_templates:
            task = WorkerTask(
                id=f"{worker_id}_{module_type}_{uuid.uuid4().hex[:6]}",
                worker_id=worker_id,
                agent_id=agent.id,
                title=task_template['title'],
                description=task_template['description'],
                task_type=task_template['type'],
                priority=task_template.get('priority', 'medium'),
                ai_guidance=task_template.get('ai_guidance', ''),
                due_date=datetime.now() + timedelta(hours=task_template.get('duration_hours', 8))
            )
            
            tasks.append(task)
            interface.active_tasks.append(task)
            self.active_tasks[task.id] = task
            agent.current_tasks.append(task.id)
        
        return tasks
    
    def _get_task_templates(self, module_type: str, worker_role: str) -> List[Dict[str, Any]]:
        """Get task templates for specific module and worker role"""
        
        task_templates = {
            'quality': {
                'inspector': [
                    {
                        'title': 'Morning Quality Inspection Round',
                        'description': 'Inspect production lines and verify quality standards',
                        'type': 'inspection',
                        'priority': 'high',
                        'duration_hours': 2,
                        'ai_guidance': 'I\'ll guide you through each inspection point and help identify potential issues.'
                    },
                    {
                        'title': 'Defect Data Collection',
                        'description': 'Record and categorize any defects found during inspection',
                        'type': 'data_entry',
                        'priority': 'medium',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll help you categorize defects and suggest root causes.'
                    },
                    {
                        'title': 'Quality Report Generation',
                        'description': 'Generate daily quality summary report',
                        'type': 'reporting',
                        'priority': 'medium',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll analyze today\'s data and help you create the report.'
                    }
                ],
                'technician': [
                    {
                        'title': 'Equipment Calibration Check',
                        'description': 'Verify measuring equipment is properly calibrated',
                        'type': 'maintenance',
                        'priority': 'high',
                        'duration_hours': 2,
                        'ai_guidance': 'I\'ll walk you through calibration procedures and log results.'
                    },
                    {
                        'title': 'Statistical Process Control',
                        'description': 'Update control charts and analyze process trends',
                        'type': 'analysis',
                        'priority': 'medium',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll help you interpret statistical data and identify trends.'
                    }
                ]
            },
            'maintenance': {
                'technician': [
                    {
                        'title': 'Preventive Maintenance Tasks',
                        'description': 'Complete scheduled PM tasks for assigned equipment',
                        'type': 'maintenance',
                        'priority': 'high',
                        'duration_hours': 4,
                        'ai_guidance': 'I\'ll provide step-by-step procedures and safety reminders.'
                    },
                    {
                        'title': 'Equipment Condition Assessment',
                        'description': 'Inspect equipment condition and record findings',
                        'type': 'inspection',
                        'priority': 'medium',
                        'duration_hours': 2,
                        'ai_guidance': 'I\'ll help you identify potential issues and predict failures.'
                    },
                    {
                        'title': 'Work Order Updates',
                        'description': 'Update status and close completed work orders',
                        'type': 'data_entry',
                        'priority': 'medium',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll help you document work performed and parts used.'
                    }
                ]
            },
            'safety': {
                'officer': [
                    {
                        'title': 'Safety Inspection Walk-through',
                        'description': 'Conduct safety inspection of work areas',
                        'type': 'inspection',
                        'priority': 'high',
                        'duration_hours': 3,
                        'ai_guidance': 'I\'ll guide you through safety checkpoints and highlight risks.'
                    },
                    {
                        'title': 'Incident Follow-up',
                        'description': 'Review and follow up on recent safety incidents',
                        'type': 'analysis',
                        'priority': 'high',
                        'duration_hours': 2,
                        'ai_guidance': 'I\'ll help analyze incident patterns and suggest preventive measures.'
                    }
                ]
            },
            'operations': {
                'operator': [
                    {
                        'title': 'Production Line Setup',
                        'description': 'Set up production line for today\'s schedule',
                        'type': 'setup',
                        'priority': 'high',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll guide you through optimal setup procedures.'
                    },
                    {
                        'title': 'Production Monitoring',
                        'description': 'Monitor production rates and quality throughout shift',
                        'type': 'monitoring',
                        'priority': 'high',
                        'duration_hours': 6,
                        'ai_guidance': 'I\'ll alert you to efficiency issues and suggest optimizations.'
                    },
                    {
                        'title': 'Shift Handover Report',
                        'description': 'Document shift performance and issues for next shift',
                        'type': 'reporting',
                        'priority': 'medium',
                        'duration_hours': 1,
                        'ai_guidance': 'I\'ll help you summarize key metrics and issues.'
                    }
                ]
            }
        }
        
        role_key = worker_role.lower().split()[-1]  # Get last word of role (inspector, technician, etc.)
        return task_templates.get(module_type, {}).get(role_key, [])
    
    async def get_worker_dashboard_data(self, worker_id: str) -> Dict[str, Any]:
        """Get dashboard data for a specific worker"""
        
        if worker_id not in self.worker_interfaces:
            return {"error": "Worker not found"}
        
        interface = self.worker_interfaces[worker_id]
        
        # Get task statistics
        total_tasks = len(interface.active_tasks)
        completed_tasks = len([t for t in interface.active_tasks if t.status == 'completed'])
        pending_tasks = len([t for t in interface.active_tasks if t.status == 'pending'])
        in_progress_tasks = len([t for t in interface.active_tasks if t.status == 'in_progress'])
        
        # Get agent status
        active_agents = len([a for a in interface.assigned_agents if a.status == 'active'])
        
        return {
            'worker_info': {
                'name': interface.name,
                'role': interface.role,
                'department': interface.department,
                'shift_status': 'on_duty'  # Would be calculated from shift_schedule
            },
            'task_summary': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'completion_rate': round((completed_tasks / max(total_tasks, 1)) * 100, 1)
            },
            'agent_summary': {
                'total_agents': len(interface.assigned_agents),
                'active_agents': active_agents,
                'available_capabilities': sum(len(a.capabilities) for a in interface.assigned_agents)
            },
            'recent_tasks': [asdict(t) for t in interface.active_tasks[-5:]],  # Last 5 tasks
            'assigned_agents': [asdict(a) for a in interface.assigned_agents]
        }
    
    async def interact_with_agent(self, worker_id: str, agent_id: str, message: str) -> str:
        """Worker interacts with their AI agent"""
        
        if agent_id not in self.worker_agents:
            return "Agent not found"
        
        agent = self.worker_agents[agent_id]
        
        if agent.worker_id != worker_id:
            return "Access denied - agent not assigned to this worker"
        
        # Update agent status
        agent.last_interaction = datetime.now()
        agent.status = 'busy'
        
        # Generate AI response based on agent's capabilities and personality
        response = await self._generate_agent_response(agent, message)
        
        # Update agent status back to active
        agent.status = 'active'
        
        return response
    
    async def _generate_agent_response(self, agent: WorkerAgent, message: str) -> str:
        """Generate AI response based on agent's personality and capabilities"""
        
        # Get agent's personality and capabilities
        personality = agent.ai_personality
        capabilities = agent.capabilities
        
        # Module-specific responses
        if agent.module_type == 'quality':
            if 'defect' in message.lower():
                return f"I see you're dealing with a defect. Based on my quality analysis capabilities, I recommend: 1) Document the defect location and type, 2) Check for similar patterns in recent production, 3) Notify the quality supervisor if it's a critical defect. What specific type of defect are you seeing?"
            elif 'inspection' in message.lower():
                return f"For your inspection, I'll guide you through the checklist: 1) Visual examination for obvious defects, 2) Dimensional checks using calibrated tools, 3) Functional testing if required. Which inspection point would you like to start with?"
        
        elif agent.module_type == 'maintenance':
            if 'repair' in message.lower() or 'fix' in message.lower():
                return f"I'll help you troubleshoot this issue. First, let's identify the symptoms: 1) When did the problem start? 2) What exactly is happening? 3) Any unusual sounds, vibrations, or readings? Once I understand the symptoms, I can guide you through the diagnostic process."
            elif 'maintenance' in message.lower():
                return f"For your maintenance task, I'll provide the procedure: 1) Safety lockout/tagout first, 2) Follow the step-by-step maintenance checklist, 3) Document all work performed and parts replaced. What equipment are you working on?"
        
        elif agent.module_type == 'safety':
            if 'hazard' in message.lower() or 'risk' in message.lower():
                return f"Safety first! I've identified potential hazards in your area. Let me help you assess the risk level: 1) Immediate danger - stop work and evacuate, 2) Moderate risk - implement controls before proceeding, 3) Low risk - document and monitor. What specific hazard are you concerned about?"
            elif 'incident' in message.lower():
                return f"For incident reporting, I'll guide you through the process: 1) Ensure everyone is safe first, 2) Secure the area, 3) Document exactly what happened, 4) Identify contributing factors, 5) Recommend corrective actions. Is anyone injured?"
        
        elif agent.module_type == 'operations':
            if 'production' in message.lower():
                return f"Let me help optimize your production process. Current metrics show: 1) Production rate analysis, 2) Quality checkpoint status, 3) Equipment efficiency. What specific production issue are you facing?"
            elif 'efficiency' in message.lower():
                return f"I can help improve efficiency. Based on today's data: 1) Identify bottlenecks, 2) Optimize workflow sequence, 3) Reduce changeover time. Which area would you like to focus on?"
        
        # Generic helpful response
        return f"I'm {agent.name}, your {agent.module_type} assistant. I can help you with: {', '.join(capabilities[:3])}. How can I assist you with your current task?"

# Global worker interface manager
worker_interface_manager = WorkerInterfaceManager()
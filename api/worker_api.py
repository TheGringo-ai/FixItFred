#!/usr/bin/env python3
"""
Worker API - Individual worker interfaces and AI agent communication
Connects workers to their personal AI agents and modules
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Import core components
from core.workers.worker_identity_system import worker_identity_system, WorkerRole
from core.identity.ai_identity_core import ai_identity_core

router = APIRouter(prefix="/api/worker", tags=["worker"])

@router.post("/create")
async def create_worker(worker_data: Dict[str, Any]):
    """Create a new worker with personal AI agent"""
    try:
        worker = await worker_identity_system.create_worker(worker_data)
        ai_agent = worker_identity_system.ai_agents[worker.ai_agent_id]
        
        return {
            "status": "success",
            "worker": {
                "worker_id": worker.worker_id,
                "name": worker.name,
                "role": worker.role.value,
                "department": worker.department,
                "ai_agent": {
                    "agent_id": ai_agent.agent_id,
                    "name": ai_agent.name,
                    "capabilities": ai_agent.expertise_domains
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{worker_id}/dashboard")
async def get_worker_dashboard(worker_id: str):
    """Get personalized dashboard for worker"""
    try:
        dashboard = await worker_identity_system.get_worker_dashboard(worker_id)
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-request")
async def process_worker_ai_request(request: Dict[str, Any]):
    """Process AI request from worker through their personal agent"""
    
    worker_id = request.get("worker_id")
    message = request.get("message")
    context = request.get("context", {})
    
    if not worker_id or not message:
        raise HTTPException(status_code=400, detail="Worker ID and message are required")
    
    try:
        response = await worker_identity_system.process_worker_request(
            worker_id, message, context
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-command")
async def process_voice_command(request: Dict[str, Any]):
    """Process voice command from worker"""
    
    worker_id = request.get("worker_id")
    command = request.get("command")
    context = request.get("context", {})
    
    if not worker_id or not command:
        raise HTTPException(status_code=400, detail="Worker ID and command are required")
    
    try:
        # Extract the actual command after "Hey Fred"
        command_lower = command.lower()
        if "hey fred" in command_lower:
            actual_command = command_lower.split("hey fred", 1)[1].strip()
            if actual_command:
                command = actual_command
        
        # Process through AI agent
        response = await worker_identity_system.process_worker_request(
            worker_id, command, {**context, "type": "voice_command"}
        )
        
        # Add voice-specific response formatting
        voice_response = {
            "understood": True,
            "response": response.get("response", "Command processed successfully."),
            "action": None,
            "params": {}
        }
        
        # Determine if there's an actionable response
        if "task" in response.get("type", ""):
            voice_response["action"] = "view_tasks"
        elif "help" in response.get("type", ""):
            voice_response["action"] = "show_help"
        elif "status" in response.get("type", ""):
            voice_response["action"] = "show_status"
        
        return voice_response
        
    except Exception as e:
        return {
            "understood": False,
            "response": "I'm sorry, I didn't understand that command. Could you try rephrasing?",
            "error": str(e)
        }

@router.get("/{worker_id}/tasks")
async def get_worker_tasks(worker_id: str):
    """Get worker's task queue"""
    try:
        tasks = worker_identity_system.task_queues.get(worker_id, [])
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{worker_id}/tasks")
async def assign_task_to_worker(worker_id: str, task: Dict[str, Any]):
    """Assign a task to worker"""
    try:
        await worker_identity_system.assign_task_to_worker(worker_id, task)
        return {"status": "success", "message": "Task assigned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{worker_id}/tasks/{task_id}")
async def update_task_status(worker_id: str, task_id: str, update: Dict[str, Any]):
    """Update task status"""
    try:
        tasks = worker_identity_system.task_queues.get(worker_id, [])
        
        for task in tasks:
            if task.get("task_id") == task_id:
                task.update(update)
                task["updated_at"] = datetime.now().isoformat()
                
                # Update worker performance metrics
                worker = worker_identity_system.workers.get(worker_id)
                if worker and update.get("status") == "completed":
                    worker.tasks_completed += 1
                    # Update efficiency score based on completion time
                    # This would be more sophisticated in production
                
                return {"status": "success", "task": task}
        
        raise HTTPException(status_code=404, detail="Task not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/{supervisor_id}")
async def get_team_overview(supervisor_id: str):
    """Get team overview for supervisors/managers"""
    try:
        team_overview = await worker_identity_system.get_team_overview(supervisor_id)
        return team_overview
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{worker_id}/performance")
async def get_worker_performance(worker_id: str):
    """Get worker performance metrics"""
    try:
        worker = worker_identity_system.workers.get(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        performance = {
            "worker_id": worker_id,
            "name": worker.name,
            "role": worker.role.value,
            "department": worker.department,
            "metrics": {
                "tasks_completed": worker.tasks_completed,
                "efficiency_score": worker.efficiency_score,
                "quality_score": worker.quality_score,
                "safety_score": worker.safety_score
            },
            "ai_agent": {
                "interactions": worker_identity_system.ai_agents[worker.ai_agent_id].interactions_count,
                "helpfulness": worker_identity_system.ai_agents[worker.ai_agent_id].helpful_rating,
                "accuracy": worker_identity_system.ai_agents[worker.ai_agent_id].accuracy_rate
            }
        }
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{worker_id}/modules/{module_name}/access")
async def request_module_access(worker_id: str, module_name: str):
    """Request access to a specific module"""
    try:
        worker = worker_identity_system.workers.get(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Check if worker is authorized for this module
        if module_name not in worker.modules_access:
            # Create access request (in production, this would go through approval)
            worker.modules_access.append(module_name)
        
        # Generate module-specific token through AI Identity Core
        from core.identity.ai_identity_core import UserClaims
        
        user_claims = ai_identity_core.user_contexts.get(worker_id)
        if user_claims:
            module_access = await ai_identity_core.authorize_module_access(
                user_claims, module_name
            )
            
            token = await ai_identity_core.issue_module_token(
                user_claims, module_access
            )
            
            return {
                "status": "success",
                "module": module_name,
                "access_token": token,
                "permissions": module_access.permissions,
                "worker_context": {
                    "role": worker.role.value,
                    "department": worker.department,
                    "specializations": worker.specializations
                }
            }
        
        raise HTTPException(status_code=403, detail="Authentication required")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{worker_id}/ai-agent")
async def get_worker_ai_agent(worker_id: str):
    """Get worker's AI agent information"""
    try:
        worker = worker_identity_system.workers.get(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        agent = worker_identity_system.ai_agents.get(worker.ai_agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="AI agent not found")
        
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "capabilities": agent.expertise_domains,
            "personality": agent.personality_traits,
            "performance": {
                "interactions": agent.interactions_count,
                "helpfulness": agent.helpful_rating,
                "accuracy": agent.accuracy_rate,
                "response_time": agent.response_time_ms
            },
            "permissions": {
                "can_execute_tasks": agent.can_execute_tasks,
                "can_make_decisions": agent.can_make_decisions,
                "can_approve_work": agent.can_approve_work
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{worker_id}/ai-agent/feedback")
async def provide_agent_feedback(worker_id: str, feedback: Dict[str, Any]):
    """Provide feedback on AI agent performance"""
    try:
        worker = worker_identity_system.workers.get(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        agent = worker_identity_system.ai_agents.get(worker.ai_agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="AI agent not found")
        
        # Update agent performance based on feedback
        rating = feedback.get("rating", 5.0)  # 1-5 scale
        helpful = feedback.get("helpful", True)
        
        # Simple learning algorithm (would be more sophisticated in production)
        if helpful:
            agent.helpful_rating = (agent.helpful_rating + rating) / 2
        else:
            agent.helpful_rating = max(1.0, agent.helpful_rating - 0.1)
        
        # Store feedback for future learning
        if not hasattr(agent, 'feedback_history'):
            agent.feedback_history = []
        
        agent.feedback_history.append({
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "helpful": helpful,
            "comment": feedback.get("comment", ""),
            "interaction_context": feedback.get("context", {})
        })
        
        return {
            "status": "success",
            "message": "Feedback recorded. AI agent will learn from this interaction."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles")
async def get_available_worker_roles():
    """Get list of available worker roles"""
    return {
        "roles": [
            {
                "name": role.value,
                "display_name": role.value.replace('_', ' ').title(),
                "description": f"{role.value.replace('_', ' ').title()} role in the organization"
            }
            for role in WorkerRole
        ]
    }

@router.get("/{worker_id}/recommendations")
async def get_worker_recommendations(worker_id: str):
    """Get AI-powered recommendations for worker"""
    try:
        worker = worker_identity_system.workers.get(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        agent = worker_identity_system.ai_agents.get(worker.ai_agent_id)
        
        # Generate personalized recommendations based on worker data
        recommendations = {
            "training": [],
            "tasks": [],
            "skills": [],
            "efficiency": []
        }
        
        # Training recommendations based on role and department
        if worker.role == WorkerRole.TECHNICIAN:
            recommendations["training"] = [
                "Advanced Troubleshooting Techniques",
                "Predictive Maintenance Fundamentals",
                "Safety Protocol Updates"
            ]
        elif worker.role == WorkerRole.OPERATOR:
            recommendations["training"] = [
                "Equipment Operation Optimization",
                "Quality Control Procedures",
                "Lean Manufacturing Principles"
            ]
        
        # Task recommendations based on current queue
        current_tasks = len(worker_identity_system.task_queues.get(worker_id, []))
        if current_tasks < 3:
            recommendations["tasks"] = [
                "Consider taking on additional preventive maintenance tasks",
                "Review pending quality inspections",
                "Check for urgent safety assessments"
            ]
        
        # Skill development recommendations
        if worker.experience_years < 2:
            recommendations["skills"] = [
                "Focus on core competencies in your role",
                "Shadow experienced team members",
                "Document your learning progress"
            ]
        elif worker.experience_years >= 5:
            recommendations["skills"] = [
                "Consider mentoring newer team members",
                "Explore leadership development opportunities",
                "Contribute to process improvements"
            ]
        
        # Efficiency recommendations based on performance
        if worker.efficiency_score < 75:
            recommendations["efficiency"] = [
                "Consider using voice commands for faster data entry",
                "Review AI agent capabilities for task automation",
                "Organize workspace for optimal workflow"
            ]
        
        return {
            "worker_id": worker_id,
            "recommendations": recommendations,
            "generated_by": agent.name,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Demo endpoints for testing
@router.post("/demo/create-sample-workers")
async def create_sample_workers():
    """Create sample workers for demo purposes"""
    
    sample_workers = [
        {
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
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@company.com",
            "role": "supervisor",
            "department": "maintenance",
            "shift": "day",
            "site": "factory-1",
            "skills": ["leadership", "planning", "problem-solving"],
            "experience_years": 10,
            "modules_access": ["chatterfix", "safety", "quality", "operations"]
        },
        {
            "name": "Mike Chen",
            "email": "mike.chen@company.com",
            "role": "operator",
            "department": "production",
            "shift": "night",
            "site": "factory-1",
            "skills": ["machine operation", "quality control", "data entry"],
            "experience_years": 3,
            "modules_access": ["operations", "quality"]
        }
    ]
    
    created_workers = []
    
    for worker_data in sample_workers:
        try:
            worker = await worker_identity_system.create_worker(worker_data)
            created_workers.append({
                "worker_id": worker.worker_id,
                "name": worker.name,
                "role": worker.role.value,
                "ai_agent": worker_identity_system.ai_agents[worker.ai_agent_id].name
            })
        except Exception as e:
            print(f"Error creating worker {worker_data['name']}: {e}")
    
    return {
        "status": "success",
        "created_workers": created_workers,
        "total": len(created_workers)
    }

if __name__ == "__main__":
    # Quick test
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
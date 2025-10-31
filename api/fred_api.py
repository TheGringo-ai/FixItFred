#!/usr/bin/env python3
"""
Fix-It Fred API - Real maintenance assistant endpoints
The practical AI that helps people fix things
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_brain.fix_it_fred_core import (
    fix_it_fred,
    Asset,
    MaintenanceTask,
    TaskPriority,
    TaskStatus
)

router = APIRouter(prefix="/api/fred", tags=["Fred"])


# Request models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    context: Optional[Dict] = None


class DiagnoseRequest(BaseModel):
    user_id: str
    asset_id: str
    problem: str


class CreateTaskRequest(BaseModel):
    user_id: str
    asset_id: str
    title: str
    description: str
    priority: str = "medium"
    due_date: Optional[str] = None


class AddAssetRequest(BaseModel):
    user_id: str
    name: str
    asset_type: str  # car, home, equipment
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None


# Endpoints
@router.post("/chat")
async def chat_with_fred(request: ChatRequest):
    """
    Natural conversation with Fred
    Example: "How do I change the oil in my truck?"
    """
    response = await fix_it_fred.chat(
        user_id=request.user_id,
        message=request.message,
        context=request.context
    )

    return {
        "response": response,
        "user_id": request.user_id,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/diagnose")
async def diagnose_problem(request: DiagnoseRequest):
    """
    Diagnose a problem with an asset
    Example: "My lawn mower won't start - cranks but doesn't fire"
    """
    diagnosis = await fix_it_fred.diagnose_problem(
        user_id=request.user_id,
        asset_id=request.asset_id,
        problem_description=request.problem
    )

    return diagnosis


@router.post("/tasks/create")
async def create_task(request: CreateTaskRequest):
    """
    Create a maintenance or repair task
    Fred will add steps, parts, tools, and estimates
    """
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "medium": TaskPriority.MEDIUM,
        "low": TaskPriority.LOW
    }

    task = await fix_it_fred.create_task(
        user_id=request.user_id,
        asset_id=request.asset_id,
        title=request.title,
        description=request.description,
        priority=priority_map.get(request.priority.lower(), TaskPriority.MEDIUM),
        due_date=request.due_date
    )

    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
        "estimated_hours": task.estimated_hours,
        "estimated_cost": task.estimated_cost,
        "parts_needed": task.parts_needed,
        "tools_needed": task.tools_needed,
        "steps": task.steps,
        "safety_notes": task.safety_notes,
        "due_date": task.due_date,
        "created_at": task.created_at
    }


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get details of a specific task"""
    task = fix_it_fred.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "estimated_hours": task.estimated_hours,
        "estimated_cost": task.estimated_cost,
        "parts_needed": task.parts_needed,
        "tools_needed": task.tools_needed,
        "steps": task.steps,
        "safety_notes": task.safety_notes,
        "due_date": task.due_date
    }


@router.get("/tasks/user/{user_id}")
async def list_user_tasks(user_id: str, status: Optional[str] = None):
    """List all tasks for a user"""
    user_tasks = [t for t in fix_it_fred.tasks.values() if t.user_id == user_id]

    if status:
        try:
            status_enum = TaskStatus(status.lower())
            user_tasks = [t for t in user_tasks if t.status == status_enum]
        except ValueError:
            pass

    return {
        "user_id": user_id,
        "tasks": [
            {
                "task_id": t.task_id,
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value,
                "due_date": t.due_date,
                "estimated_cost": t.estimated_cost
            }
            for t in user_tasks
        ]
    }


@router.post("/assets/add")
async def add_asset(request: AddAssetRequest):
    """
    Add an asset (car, home, equipment) to track
    """
    asset_id = f"{request.user_id}_{request.asset_type}_{datetime.now().timestamp()}"

    asset = Asset(
        asset_id=asset_id,
        name=request.name,
        asset_type=request.asset_type,
        make=request.make,
        model=request.model,
        year=request.year
    )

    fix_it_fred.assets[asset_id] = asset

    return {
        "asset_id": asset_id,
        "name": asset.name,
        "type": asset.asset_type,
        "make": asset.make,
        "model": asset.model,
        "year": asset.year
    }


@router.get("/assets/user/{user_id}")
async def list_user_assets(user_id: str):
    """List all assets for a user"""
    user_assets = [a for a in fix_it_fred.assets.values() if a.asset_id.startswith(user_id)]

    return {
        "user_id": user_id,
        "assets": [
            {
                "asset_id": a.asset_id,
                "name": a.name,
                "type": a.asset_type,
                "make": a.make,
                "model": a.model,
                "year": a.year
            }
            for a in user_assets
        ]
    }


@router.get("/schedule/{asset_id}")
async def get_maintenance_schedule(asset_id: str):
    """
    Get recommended maintenance schedule for an asset
    """
    schedule = await fix_it_fred.get_maintenance_schedule(
        user_id="",  # Extract from asset_id
        asset_id=asset_id
    )

    return {
        "asset_id": asset_id,
        "schedule": schedule
    }


@router.post("/parts/order/{task_id}")
async def order_parts(task_id: str, auto_order: bool = False):
    """
    Get parts sourcing for a task
    """
    result = await fix_it_fred.order_parts(task_id, auto_order)

    return result


# Quick examples endpoint
@router.get("/examples")
async def get_examples():
    """Example interactions with Fred"""
    return {
        "chat_examples": [
            "How do I change the oil in my 2015 Ford F-150?",
            "My lawn mower won't start - it cranks but doesn't fire",
            "Plan a bathroom remodel with materials list",
            "Build a workbench - give me a cut list",
            "What should I check for 100k mile service on my Camry?"
        ],
        "task_examples": [
            {
                "title": "Change engine oil",
                "description": "Regular oil change service"
            },
            {
                "title": "Replace air filter",
                "description": "Air filter replacement due"
            },
            {
                "title": "Repair leaky faucet",
                "description": "Kitchen faucet dripping"
            }
        ],
        "asset_types": [
            "car",
            "truck",
            "motorcycle",
            "home",
            "lawn_mower",
            "generator",
            "appliance"
        ]
    }

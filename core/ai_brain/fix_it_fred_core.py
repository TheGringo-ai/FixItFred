#!/usr/bin/env python3
"""
Fix-It Fred - The Intelligent Maintenance and DIY Assistant
The AI brain that helps real people fix real things
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"  # Safety issue, breakdown
    HIGH = "high"         # Overdue maintenance
    MEDIUM = "medium"     # Scheduled maintenance
    LOW = "low"          # Optional improvements


class TaskStatus(Enum):
    """Task completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"


@dataclass
class Asset:
    """User's asset (car, home, equipment)"""
    asset_id: str
    name: str
    asset_type: str  # car, home, equipment, appliance
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[str] = None
    last_service: Optional[str] = None
    notes: str = ""


@dataclass
class MaintenanceTask:
    """A maintenance or repair task"""
    task_id: str
    user_id: str
    asset_id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[str] = None
    estimated_hours: float = 1.0
    estimated_cost: float = 0.0
    parts_needed: List[Dict[str, Any]] = None
    tools_needed: List[str] = None
    steps: List[str] = None
    safety_notes: List[str] = None
    completed_date: Optional[str] = None
    created_at: str = None


@dataclass
class Part:
    """A part or material needed"""
    part_id: str
    name: str
    part_number: Optional[str] = None
    quantity: int = 1
    unit: str = "each"
    estimated_cost: float = 0.0
    suppliers: List[Dict[str, Any]] = None
    ordered: bool = False
    received: bool = False


class FixItFredCore:
    """
    The intelligent AI brain for Fix-It Fred
    Helps users diagnose, schedule, and complete maintenance tasks
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Initialize Fred with optional AI API keys"""
        self.api_keys = api_keys or {}

        # AI clients
        self.openai_client = None
        self.anthropic_client = None

        # Initialize AI if keys available
        if OPENAI_AVAILABLE and 'openai' in self.api_keys:
            self.openai_client = openai.AsyncOpenAI(api_key=self.api_keys['openai'])
        if ANTHROPIC_AVAILABLE and 'anthropic' in self.api_keys:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.api_keys['anthropic'])

        # In-memory storage (replace with database)
        self.users: Dict[str, Dict] = {}
        self.assets: Dict[str, Asset] = {}
        self.tasks: Dict[str, MaintenanceTask] = {}
        self.parts: Dict[str, Part] = {}

    async def think(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Fred's thinking - uses AI when available, falls back to logic
        """
        # Try Claude first (better at practical reasoning)
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    system=self._get_system_prompt(),
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return response.content[0].text
            except Exception as e:
                print(f"Claude error: {e}")

        # Try GPT-4 as fallback
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"GPT-4 error: {e}")

        # Fallback to rule-based
        return self._rule_based_response(prompt, context)

    def _get_system_prompt(self) -> str:
        """Fred's personality and capabilities"""
        return """You are Fix-It Fred, the intelligent maintenance and DIY assistant.

Your mission: Help real people fix real things.
- Cars, homes, equipment, appliances
- Maintenance, repairs, projects, troubleshooting

Your personality:
- Smart but approachable
- Mechanically inclined and practical
- Like a reliable shop buddy, not a corporate bot
- Clear, safe, and resourceful

You provide:
1. Diagnostic help (troubleshooting)
2. Step-by-step repair guides
3. Parts lists and cost estimates
4. Tool recommendations
5. Safety warnings
6. Maintenance schedules
7. Project planning

Always prioritize safety. Be specific with part numbers, torque specs, and procedures.
Speak plainly - no jargon unless necessary."""

    def _rule_based_response(self, prompt: str, context: Optional[Dict]) -> str:
        """Simple rule-based responses when AI unavailable"""
        prompt_lower = prompt.lower()

        # Common maintenance questions
        if "oil change" in prompt_lower:
            return """I can help with that oil change!

Typical oil change requires:
- 4-6 quarts of oil (check your manual for exact amount)
- New oil filter
- Drain pan
- Wrench for drain plug
- Oil filter wrench
- Funnel

Basic steps:
1. Warm up engine (5 mins)
2. Lift vehicle safely
3. Place drain pan under plug
4. Remove drain plug, drain oil
5. Replace drain plug with new washer
6. Remove old filter
7. Lubricate new filter gasket
8. Install new filter hand-tight
9. Add new oil per spec
10. Check level, run engine, check for leaks

Need specific help for your vehicle?"""

        if "won't start" in prompt_lower:
            return """Let's troubleshoot why it won't start.

First, tell me:
1. Does it crank (engine turns over)?
2. Any unusual sounds?
3. When did it last run?
4. Any warning lights?

Common causes:
- Dead battery (most common)
- Bad starter
- No fuel
- No spark
- Timing issue

Let's narrow it down - answer those questions and I'll guide you through checks."""

        return "I can help with that! Can you give me more details about what you're working on?"

    async def diagnose_problem(
        self,
        user_id: str,
        asset_id: str,
        problem_description: str
    ) -> Dict[str, Any]:
        """
        Diagnose a problem and suggest solutions
        """
        asset = self.assets.get(asset_id)
        if not asset:
            return {"error": "Asset not found"}

        # Build diagnostic prompt
        prompt = f"""User reports a problem:
Asset: {asset.name} ({asset.make} {asset.model} {asset.year if asset.year else ''})
Problem: {problem_description}

Provide:
1. Most likely causes (ranked by probability)
2. How to test/confirm each cause
3. Parts typically needed
4. Estimated difficulty (easy/medium/hard)
5. Safety warnings
6. Estimated cost

Format as JSON."""

        diagnosis = await self.think(prompt)

        try:
            result = json.loads(diagnosis)
        except:
            # Parse as best we can or return text
            result = {
                "diagnosis": diagnosis,
                "asset": asdict(asset)
            }

        return result

    async def create_task(
        self,
        user_id: str,
        asset_id: str,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Create a maintenance or repair task
        """
        task_id = str(uuid.uuid4())[:8]

        # Use AI to enhance task details
        prompt = f"""Task: {title}
Description: {description}

Provide:
1. Step-by-step instructions (5-10 steps)
2. Parts needed (name, quantity, est. cost)
3. Tools needed
4. Safety notes
5. Estimated time
6. Estimated cost

Format as JSON."""

        details = await self.think(prompt)

        try:
            parsed = json.loads(details)
            steps = parsed.get('steps', [])
            parts = parsed.get('parts', [])
            tools = parsed.get('tools', [])
            safety = parsed.get('safety', [])
            est_hours = parsed.get('estimated_hours', 2.0)
            est_cost = parsed.get('estimated_cost', 50.0)
        except:
            steps = [description]
            parts = []
            tools = []
            safety = []
            est_hours = 2.0
            est_cost = 50.0

        task = MaintenanceTask(
            task_id=task_id,
            user_id=user_id,
            asset_id=asset_id,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            due_date=due_date,
            estimated_hours=est_hours,
            estimated_cost=est_cost,
            parts_needed=parts,
            tools_needed=tools,
            steps=steps,
            safety_notes=safety,
            created_at=datetime.now().isoformat()
        )

        self.tasks[task_id] = task
        return task

    async def get_maintenance_schedule(
        self,
        user_id: str,
        asset_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get recommended maintenance schedule for an asset
        """
        asset = self.assets.get(asset_id)
        if not asset:
            return []

        prompt = f"""Create maintenance schedule for:
{asset.asset_type}: {asset.make} {asset.model} {asset.year if asset.year else ''}

List routine maintenance tasks with:
- Task name
- Interval (miles or months)
- Priority
- Estimated cost
- Why it's important

Common intervals: oil change, filters, fluids, brakes, tires, etc."""

        schedule = await self.think(prompt)

        # Parse and structure
        try:
            items = json.loads(schedule)
        except:
            items = [{"task": "Maintenance schedule", "details": schedule}]

        return items

    async def order_parts(
        self,
        task_id: str,
        auto_order: bool = False
    ) -> Dict[str, Any]:
        """
        Help user order parts for a task
        """
        task = self.tasks.get(task_id)
        if not task or not task.parts_needed:
            return {"error": "No parts needed"}

        # Find suppliers for each part
        parts_with_suppliers = []
        for part in task.parts_needed:
            part_name = part.get('name', '')

            # Use AI to find suppliers (in real system, use parts APIs)
            prompt = f"""Find suppliers for: {part_name}
Quantity: {part.get('quantity', 1)}

Provide top 3 options with:
- Store name
- Price
- Availability
- URL or location"""

            suppliers = await self.think(prompt)
            parts_with_suppliers.append({
                "part": part,
                "suppliers": suppliers
            })

        return {
            "task_id": task_id,
            "task_title": task.title,
            "parts": parts_with_suppliers,
            "total_estimate": task.estimated_cost
        }

    async def chat(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Natural conversation with Fred
        """
        # Get user's assets for context
        user_assets = [a for a in self.assets.values() if a.asset_id.startswith(user_id)]

        context_str = ""
        if user_assets:
            context_str = "\nUser's assets: " + ", ".join([f"{a.name} ({a.make} {a.model})" for a in user_assets])

        prompt = f"""{context_str}

User says: {message}

Respond as Fred - helpful, practical, clear."""

        response = await self.think(prompt, context)
        return response


# Global Fred instance
fix_it_fred = FixItFredCore()

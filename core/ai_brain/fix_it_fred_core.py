#!/usr/bin/env python3
"""
Fix-It Fred - The Intelligent Maintenance and DIY Assistant
Enhanced with Grok AI Team Integration and Voice Commands
The AI brain that helps real people fix real things
"""

import asyncio
import json
import uuid
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import AI team integration
try:
    from .ai_team_integration import FixItFredAITeam, FixItFredTaskType

    AI_TEAM_AVAILABLE = True
except ImportError:
    AI_TEAM_AVAILABLE = False

try:
    import speech_recognition as sr
    import pyttsx3

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = "critical"  # Safety issue, breakdown
    HIGH = "high"  # Overdue maintenance
    MEDIUM = "medium"  # Scheduled maintenance
    LOW = "low"  # Optional improvements


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


class VoiceCommand(Enum):
    """Voice command types"""

    DIAGNOSE = "diagnose"
    CREATE_TASK = "create_task"
    CHECK_STATUS = "check_status"
    ORDER_PARTS = "order_parts"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"
    CHAT = "chat"
    HELP = "help"


class FixItFredCore:
    """
    The intelligent AI brain for Fix-It Fred
    Enhanced with Grok AI Team Integration and Voice Commands
    Helps users diagnose, schedule, and complete maintenance tasks
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Initialize Fred with optional AI API keys"""
        self.api_keys = api_keys or {}

        # AI Team Integration
        self.ai_team = None
        if AI_TEAM_AVAILABLE:
            self.ai_team = FixItFredAITeam(
                grok_api_key=self.api_keys.get("grok") or os.getenv("XAI_API_KEY"),
                openai_api_key=self.api_keys.get("openai")
                or os.getenv("OPENAI_API_KEY"),
                anthropic_api_key=self.api_keys.get("anthropic")
                or os.getenv("ANTHROPIC_API_KEY"),
                gemini_api_key=self.api_keys.get("gemini")
                or os.getenv("GEMINI_API_KEY"),
            )
            logger.info("🤖 AI Team integrated successfully")
        else:
            logger.warning("⚠️ AI Team integration not available")

        # Legacy AI clients (fallback)
        self.openai_client = None
        self.anthropic_client = None

        # Initialize legacy AI if keys available
        if OPENAI_AVAILABLE and "openai" in self.api_keys:
            self.openai_client = openai.AsyncOpenAI(api_key=self.api_keys["openai"])
        if ANTHROPIC_AVAILABLE and "anthropic" in self.api_keys:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.api_keys["anthropic"]
            )

        # Voice system
        self.voice_engine = None
        self.voice_recognizer = None
        if VOICE_AVAILABLE:
            try:
                self.voice_engine = pyttsx3.init()
                self.voice_recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("🎤 Voice system initialized")
            except Exception as e:
                logger.warning(f"⚠️ Voice system failed to initialize: {e}")

        # In-memory storage (replace with database)
        self.users: Dict[str, Dict] = {}
        self.assets: Dict[str, Asset] = {}
        self.tasks: Dict[str, MaintenanceTask] = {}
        self.parts: Dict[str, Part] = {}

        # Voice command state
        self.listening_for_commands = False
        self.wake_words = ["hey fred", "fix it fred", "fred"]

    async def think(
        self, prompt: str, context: Optional[Dict] = None, task_type: str = "general"
    ) -> str:
        """
        Fred's enhanced thinking - uses AI Team when available, falls back to legacy AI
        """
        # Use AI Team first (multi-AI collaboration)
        if self.ai_team:
            try:
                # Map task types to FixItFred task types
                task_type_mapping = {
                    "diagnosis": FixItFredTaskType.DIAGNOSIS,
                    "repair": FixItFredTaskType.REPAIR,
                    "optimization": FixItFredTaskType.OPTIMIZATION,
                    "troubleshooting": FixItFredTaskType.TROUBLESHOOTING,
                    "general": FixItFredTaskType.ANALYSIS,
                }

                fred_task_type = task_type_mapping.get(
                    task_type, FixItFredTaskType.ANALYSIS
                )

                # Get AI team collaboration
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type=fred_task_type, include_reasoning=True
                )

                # Get the best response
                best_response = max(responses.values(), key=lambda x: x.confidence)
                logger.info(
                    f"🤖 AI Team response from {best_response.provider.value} (confidence: {best_response.confidence:.2f})"
                )

                return best_response.content

            except Exception as e:
                logger.error(f"AI Team error: {e}")

        # Try Claude first (better at practical reasoning) - Legacy fallback
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    system=self._get_system_prompt(),
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Claude error: {e}")

        # Try GPT-4 as fallback
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"GPT-4 error: {e}")

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
        self, user_id: str, asset_id: str, problem_description: str
    ) -> Dict[str, Any]:
        """
        Enhanced diagnosis using AI team collaboration
        """
        asset = self.assets.get(asset_id)
        if not asset:
            return {"error": "Asset not found"}

        # Use AI team for diagnosis if available
        if self.ai_team:
            try:
                # Build diagnostic context
                context = {
                    "asset_type": asset.asset_type,
                    "make": asset.make,
                    "model": asset.model,
                    "year": asset.year,
                    "service_history": asset.last_service,
                }

                # Get AI team diagnosis
                diagnosis_responses = await self.ai_team.diagnose_with_ai_team(
                    problem_description, context
                )

                # Get fix plan from best diagnosis
                best_diagnosis = max(
                    diagnosis_responses.values(), key=lambda x: x.confidence
                )
                fix_plan = await self.ai_team.generate_fix_plan(
                    problem_description, diagnosis_responses
                )

                return {
                    "diagnosis": best_diagnosis.content,
                    "confidence": best_diagnosis.confidence,
                    "ai_provider": best_diagnosis.provider.value,
                    "fix_plan": fix_plan,
                    "fix_instructions": best_diagnosis.fix_instructions,
                    "asset": asdict(asset),
                    "all_responses": {
                        k: v.content for k, v in diagnosis_responses.items()
                    },
                }

            except Exception as e:
                logger.error(f"AI team diagnosis error: {e}")

        # Fallback to original method
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

        diagnosis = await self.think(prompt, task_type="diagnosis")

        try:
            result = json.loads(diagnosis)
        except:
            # Parse as best we can or return text
            result = {"diagnosis": diagnosis, "asset": asdict(asset)}

        return result

    async def speak(self, text: str) -> None:
        """Make Fred speak using text-to-speech"""
        if self.voice_engine:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                logger.error(f"Speech error: {e}")
        else:
            logger.info(f"Fred says: {text}")

    async def listen_for_wake_word(self) -> bool:
        """Listen for wake words like 'Hey Fred'"""
        if not self.voice_recognizer or not self.microphone:
            return False

        try:
            with self.microphone as source:
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("🎤 Listening for wake word...")

            with self.microphone as source:
                audio = self.voice_recognizer.listen(
                    source, timeout=5, phrase_time_limit=3
                )

            text = self.voice_recognizer.recognize_google(audio).lower()

            for wake_word in self.wake_words:
                if wake_word in text:
                    logger.info(f"🎤 Wake word detected: {wake_word}")
                    return True

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")

        return False

    async def listen_for_command(self) -> Optional[str]:
        """Listen for voice command after wake word"""
        if not self.voice_recognizer or not self.microphone:
            return None

        try:
            await self.speak("Yes? How can I help you?")

            with self.microphone as source:
                logger.info("🎤 Listening for command...")
                audio = self.voice_recognizer.listen(
                    source, timeout=10, phrase_time_limit=10
                )

            command = self.voice_recognizer.recognize_google(audio)
            logger.info(f"🎤 Command received: {command}")
            return command

        except sr.WaitTimeoutError:
            await self.speak("I didn't hear anything. Try again with 'Hey Fred'")
        except sr.UnknownValueError:
            await self.speak("I didn't understand that. Could you repeat?")
        except Exception as e:
            logger.error(f"Voice command error: {e}")
            await self.speak("Sorry, I had trouble hearing you.")

        return None

    async def process_voice_command(
        self, command: str, user_id: str = "voice_user"
    ) -> str:
        """Process voice command and execute appropriate action"""
        command_lower = command.lower()

        # Parse command type
        if any(
            word in command_lower for word in ["diagnose", "problem", "issue", "broken"]
        ):
            await self.speak(
                "What's the problem? Tell me about your asset and what's wrong."
            )
            # In a real implementation, continue listening for the problem description
            return "Diagnosis mode activated. Please describe the problem."

        elif any(
            word in command_lower for word in ["create task", "add task", "schedule"]
        ):
            await self.speak("I'll help you create a task. What needs to be done?")
            return "Task creation mode activated."

        elif any(word in command_lower for word in ["status", "tasks", "what's due"]):
            # Get user's pending tasks
            user_tasks = [
                t
                for t in self.tasks.values()
                if t.user_id == user_id and t.status == TaskStatus.PENDING
            ]
            if user_tasks:
                response = f"You have {len(user_tasks)} pending tasks. "
                for task in user_tasks[:3]:  # Limit to 3 tasks
                    response += f"{task.title}, "
                await self.speak(response)
                return response
            else:
                await self.speak("You have no pending tasks. Great job!")
                return "No pending tasks."

        elif any(word in command_lower for word in ["help", "what can you do"]):
            help_text = "I can help you diagnose problems, create maintenance tasks, check your schedule, order parts, and chat about repairs. Just say 'Hey Fred' and tell me what you need!"
            await self.speak(help_text)
            return help_text

        else:
            # General chat
            response = await self.chat(user_id, command)
            await self.speak(response)
            return response

    async def start_voice_assistant(self, user_id: str = "voice_user") -> None:
        """Start the voice assistant loop"""
        if not VOICE_AVAILABLE:
            logger.error("Voice system not available")
            return

        logger.info("🎤 Starting voice assistant - say 'Hey Fred' to wake me up")
        await self.speak("Voice assistant ready. Say 'Hey Fred' when you need help.")

        self.listening_for_commands = True

        while self.listening_for_commands:
            try:
                # Listen for wake word
                if await self.listen_for_wake_word():
                    # Listen for command
                    command = await self.listen_for_command()
                    if command:
                        # Process command
                        await self.process_voice_command(command, user_id)

                await asyncio.sleep(1)  # Brief pause

            except KeyboardInterrupt:
                logger.info("Voice assistant stopped by user")
                break
            except Exception as e:
                logger.error(f"Voice assistant error: {e}")

        await self.speak("Voice assistant stopped. Goodbye!")

    def stop_voice_assistant(self):
        """Stop the voice assistant"""
        self.listening_for_commands = False

    async def create_task(
        self,
        user_id: str,
        asset_id: str,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None,
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
            steps = parsed.get("steps", [])
            parts = parsed.get("parts", [])
            tools = parsed.get("tools", [])
            safety = parsed.get("safety", [])
            est_hours = parsed.get("estimated_hours", 2.0)
            est_cost = parsed.get("estimated_cost", 50.0)
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
            created_at=datetime.now().isoformat(),
        )

        self.tasks[task_id] = task
        return task

    async def get_maintenance_schedule(
        self, user_id: str, asset_id: str
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
        self, task_id: str, auto_order: bool = False
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
            part_name = part.get("name", "")

            # Use AI to find suppliers (in real system, use parts APIs)
            prompt = f"""Find suppliers for: {part_name}
Quantity: {part.get('quantity', 1)}

Provide top 3 options with:
- Store name
- Price
- Availability
- URL or location"""

            suppliers = await self.think(prompt)
            parts_with_suppliers.append({"part": part, "suppliers": suppliers})

        return {
            "task_id": task_id,
            "task_title": task.title,
            "parts": parts_with_suppliers,
            "total_estimate": task.estimated_cost,
        }

    async def chat(
        self, user_id: str, message: str, context: Optional[Dict] = None
    ) -> str:
        """
        Natural conversation with Fred
        """
        # Get user's assets for context
        user_assets = [
            a for a in self.assets.values() if a.asset_id.startswith(user_id)
        ]

        context_str = ""
        if user_assets:
            context_str = "\nUser's assets: " + ", ".join(
                [f"{a.name} ({a.make} {a.model})" for a in user_assets]
            )

        prompt = f"""{context_str}

User says: {message}

Respond as Fred - helpful, practical, clear."""

        response = await self.think(prompt, context)
        return response


# Global Fred instance
fix_it_fred = FixItFredCore()

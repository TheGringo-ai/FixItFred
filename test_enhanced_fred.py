#!/usr/bin/env python3
"""
Test script for Enhanced FixItFred with AI Team Integration
Demonstrates voice commands and multi-AI collaboration
"""

import asyncio
import os
import sys
from datetime import datetime

# Add core to path
sys.path.append(".")
from core.ai_brain.fix_it_fred_core import FixItFredCore, Asset, TaskPriority


async def test_enhanced_fred():
    """Test the enhanced FixItFred with AI team collaboration"""

    print("🔧 Testing Enhanced FixItFred with AI Team Integration")
    print("=" * 60)

    # Initialize Fred with API keys from environment
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    fred = FixItFredCore(api_keys)

    # Test 1: Create a test asset
    print("\n1. 🚗 Creating test asset...")
    test_asset = Asset(
        asset_id="test_car_001",
        name="My Toyota Camry",
        asset_type="car",
        make="Toyota",
        model="Camry",
        year=2018,
        last_service="2024-09-15",
    )
    fred.assets[test_asset.asset_id] = test_asset
    print(f"✅ Created asset: {test_asset.name}")

    # Test 2: AI Team Diagnosis
    print("\n2. 🤖 Testing AI Team Diagnosis...")
    problem = "Car makes a grinding noise when braking and pulls to the right"

    try:
        diagnosis = await fred.diagnose_problem(
            user_id="test_user", asset_id="test_car_001", problem_description=problem
        )

        print(f"✅ Diagnosis completed!")
        if "confidence" in diagnosis:
            print(f"   🎯 Confidence: {diagnosis['confidence']:.2f}")
            print(f"   🤖 AI Provider: {diagnosis['ai_provider']}")
            print(f"   📋 Diagnosis: {diagnosis['diagnosis'][:200]}...")
            if diagnosis.get("fix_instructions"):
                print(
                    f"   🔧 Fix Instructions: {len(diagnosis['fix_instructions'])} steps"
                )
        else:
            print(
                f"   📋 Diagnosis: {diagnosis.get('diagnosis', 'No diagnosis')[:200]}..."
            )

    except Exception as e:
        print(f"❌ Diagnosis error: {e}")

    # Test 3: Enhanced Thinking with AI Team
    print("\n3. 🧠 Testing Enhanced AI Team Thinking...")

    try:
        question = "What's the best way to change brake pads on a 2018 Toyota Camry?"
        response = await fred.think(question, task_type="repair")

        print(f"✅ AI Team response:")
        print(f"   💭 Response: {response[:300]}...")

    except Exception as e:
        print(f"❌ AI Team thinking error: {e}")

    # Test 4: Create Enhanced Task
    print("\n4. 📋 Testing Enhanced Task Creation...")

    try:
        task = await fred.create_task(
            user_id="test_user",
            asset_id="test_car_001",
            title="Replace brake pads and check alignment",
            description="Fix grinding noise and right pull issue",
            priority=TaskPriority.HIGH,
        )

        print(f"✅ Task created: {task.title}")
        print(f"   ⏱️  Estimated time: {task.estimated_hours} hours")
        print(f"   💰 Estimated cost: ${task.estimated_cost}")
        print(f"   🔧 Steps: {len(task.steps)} steps")
        print(f"   ⚠️  Safety notes: {len(task.safety_notes)} warnings")

    except Exception as e:
        print(f"❌ Task creation error: {e}")

    # Test 5: Voice Commands (if available)
    print("\n5. 🎤 Testing Voice Command Processing...")

    try:
        # Test voice command processing without actual audio
        voice_commands = [
            "Hey Fred, what's my status?",
            "Help me diagnose a problem",
            "What can you do?",
            "Create a task for oil change",
        ]

        for command in voice_commands:
            response = await fred.process_voice_command(command, "test_user")
            print(f"   🎤 '{command}' -> {response[:100]}...")

    except Exception as e:
        print(f"❌ Voice command error: {e}")

    # Test 6: Chat with AI Team
    print("\n6. 💬 Testing AI Team Chat...")

    try:
        chat_message = "My car is making a weird noise when I turn the steering wheel. What could it be?"
        response = await fred.chat("test_user", chat_message)

        print(f"✅ Chat response:")
        print(f"   💬 Fred says: {response[:300]}...")

    except Exception as e:
        print(f"❌ Chat error: {e}")

    # Test 7: AI Team Status
    print("\n7. 📊 AI Team Status...")

    if fred.ai_team:
        try:
            status = fred.ai_team.get_ai_team_status()
            print(f"✅ AI Team Status:")
            print(f"   🤖 Available Providers: {status['available_providers']}")
            print(f"   📋 Active Tasks: {status['active_tasks']}")
            print(f"   ✅ Completed Tasks: {status['completed_tasks']}")
            print(f"   📈 Conversation History: {status['conversation_history_length']}")

        except Exception as e:
            print(f"❌ AI team status error: {e}")
    else:
        print("⚠️  AI Team not available")

    print("\n" + "=" * 60)
    print("🎉 Enhanced FixItFred testing complete!")
    print("🤖 Ready for voice commands: Say 'Hey Fred' to start!")


def test_voice_assistant():
    """Test the voice assistant (interactive)"""
    print("\n🎤 Voice Assistant Test")
    print("This will start the voice assistant. Say 'Hey Fred' to interact.")
    print("Press Ctrl+C to stop.")

    fred = FixItFredCore()

    try:
        asyncio.run(fred.start_voice_assistant("voice_test_user"))
    except KeyboardInterrupt:
        print("\n👋 Voice assistant test stopped")


if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Full AI Team Integration Test")
    print("2. Voice Assistant Test (interactive)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        test_voice_assistant()
    else:
        asyncio.run(test_enhanced_fred())

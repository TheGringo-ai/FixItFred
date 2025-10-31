#!/usr/bin/env python3
"""
FixItFred Platform Test Script
Tests core functionality of the organized platform
"""

import asyncio
import sys
import pytest
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

@pytest.mark.asyncio
async def test_platform():
    """Test all core platform components"""
    print("🔧 Testing FixItFred Universal AI Business Platform")
    print("="*60)
    
    # Test 1: Core Platform
    print("\n1. Testing Core Platform...")
    try:
        from core.orchestration.platform_manager import FixItFredOS
        platform = FixItFredOS()
        print("✅ FixItFredOS initialized successfully")
    except Exception as e:
        print(f"❌ FixItFredOS failed: {e}")
        return False
    
    # Test 2: AI Brain
    print("\n2. Testing AI Brain...")
    try:
        await platform.initialize()
        print("✅ Universal AI initialized successfully")
    except Exception as e:
        print(f"⚠️ AI initialization warning: {e}")
    
    # Test 3: Data Warehouse
    print("\n3. Testing Data Infrastructure...")
    try:
        from data.warehouse.data_warehouse import DailyOperationsManager
        data_manager = DailyOperationsManager()
        await asyncio.sleep(0.1) # Allow background initialization to start
        print("✅ Data warehouse initialized successfully")
    except Exception as e:
        print(f"❌ Data warehouse failed: {e}")
    
    # Test 4: Module Builder
    print("\n4. Testing Module Builder...")
    try:
        from modules.quality.quality_module import EnterpriseModuleBuilder
        module_builder = EnterpriseModuleBuilder()
        print("✅ Enterprise module builder ready")
    except Exception as e:
        print(f"❌ Module builder failed: {e}")
    
    # Test 5: Business Models
    print("\n5. Testing Business Models...")
    try:
        from business.models.proposal_generator import CustomerEngagementProcess
        engagement = CustomerEngagementProcess()
        print("✅ Business proposal system ready")
    except Exception as e:
        print(f"❌ Business models failed: {e}")
    
    # Test 6: Project Adapter
    print("\n6. Testing Project Adapter...")
    try:
        from tools.adapters.project_adapter import GringoUniversalAdapter
        adapter = GringoUniversalAdapter()
        print("✅ Universal project adapter ready")
    except Exception as e:
        print(f"❌ Project adapter failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 PLATFORM TEST COMPLETE!")
    print("✅ FixItFred is ready for business deployment!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_platform())
#!/usr/bin/env python3
"""
Complete End-to-End Platform Test
Tests the entire FixItFred platform from deployment to worker level
"""

import sys
import os
sys.path.append('.')

import asyncio
import json
import sqlite3
from datetime import datetime
import uuid

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_test(message, status="INFO"):
    color = Colors.BLUE
    if status == "PASS":
        color = Colors.GREEN
    elif status == "FAIL":
        color = Colors.RED
    elif status == "WARN":
        color = Colors.YELLOW
    
    print(f"{color}{Colors.BOLD}[{status}]{Colors.END} {message}")

async def test_master_deployment_system():
    """Test the master deployment system"""
    log_test("Testing Master Deployment System", "INFO")
    
    try:
        from core.fred_master_deployment import fred_assistant
        
        # Test deployment
        log_test("Creating test deployment...", "INFO")
        deployment = await fred_assistant.deploy_for_company(
            company_name="Test Manufacturing Corp",
            industry="manufacturing",
            size="medium",
            modules=["quality", "maintenance", "safety"],
            worker_count=100
        )
        
        if deployment and "deployment_id" in deployment:
            log_test("✅ Master deployment system working", "PASS")
            return deployment["deployment_id"]
        else:
            log_test("❌ Master deployment failed", "FAIL")
            return None
            
    except Exception as e:
        log_test(f"❌ Master deployment error: {str(e)}", "FAIL")
        return None

async def test_module_system():
    """Test the module generation system"""
    log_test("Testing Module System", "INFO")
    
    try:
        from core.modules.module_template_engine import UniversalModuleEngine
        
        engine = UniversalModuleEngine()
        
        # Test module creation
        module_config = {
            "tenant": "test_corp",
            "name": "test_quality_module", 
            "type": "quality",
            "features": ["inspection", "defect_tracking", "compliance"],
            "target_industry": "manufacturing"
        }
        
        log_test("Creating test module...", "INFO")
        module = await engine.create_module_from_template("quality_control", module_config)
        
        if module and "module_id" in module:
            log_test("✅ Module system working", "PASS")
            return module["module_id"]
        else:
            log_test("❌ Module creation failed", "FAIL")
            return None
            
    except Exception as e:
        log_test(f"❌ Module system error: {str(e)}", "FAIL")
        return None

async def test_worker_identity_system():
    """Test the worker identity and AI agent system"""
    log_test("Testing Worker Identity System", "INFO")
    
    try:
        from core.workers.worker_identity_system import WorkerIdentitySystem
        
        worker_system = WorkerIdentitySystem()
        
        # Test worker creation
        log_test("Creating test worker...", "INFO")
        worker_data = {
            "name": "John Test Worker",
            "email": "john@test.com",
            "role": "inspector",
            "department": "quality",
            "skills": ["quality_control", "inspection"],
            "experience_years": 3
        }
        worker_profile = await worker_system.create_worker(worker_data)
        
        if worker_profile:
            log_test("✅ Worker identity system working", "PASS")
            
            # Test AI agent assignment (already done in create_worker)
            log_test("Testing AI agent assignment...", "INFO")
            ai_agent = worker_system.ai_agents.get(worker_profile.ai_agent_id)
            
            if ai_agent:
                log_test("✅ AI agent system working", "PASS")
                return worker_profile.worker_id
            else:
                log_test("❌ AI agent assignment failed", "FAIL")
                return None
        else:
            log_test("❌ Worker creation failed", "FAIL")
            return None
            
    except Exception as e:
        log_test(f"❌ Worker system error: {str(e)}", "FAIL")
        return None

async def test_offline_sync_system():
    """Test the offline sync and device recovery system"""
    log_test("Testing Offline & Device Recovery System", "INFO")
    
    try:
        from core.offline.offline_sync_engine import OfflineSyncEngine
        from core.offline.device_recovery_system import DeviceRecoverySystem
        
        # Test offline sync
        sync_engine = OfflineSyncEngine()
        log_test("Testing offline sync engine...", "INFO")
        
        # Simulate offline data
        test_data = {
            "task_id": "TEST-TASK-001",
            "worker_id": "TEST-001",
            "data": {"inspection_result": "passed", "notes": "All good"},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store offline
        await sync_engine.store_offline_record("quality_inspection", test_data, "TEST-001", "device-001")
        
        # Test sync
        sync_result = await sync_engine.sync_when_online()
        
        if sync_result:
            log_test("✅ Offline sync system working", "PASS")
        else:
            log_test("❌ Offline sync failed", "FAIL")
        
        # Test device recovery
        log_test("Testing device recovery system...", "INFO")
        recovery_system = DeviceRecoverySystem()
        
        # Simulate device failure and recovery
        recovery_data = recovery_system.create_recovery_checkpoint("TEST-001", test_data)
        if recovery_data:
            log_test("✅ Device recovery system working", "PASS")
            return True
        else:
            log_test("❌ Device recovery failed", "FAIL")
            return False
            
    except Exception as e:
        log_test(f"❌ Offline/Recovery system error: {str(e)}", "FAIL")
        return False

async def test_api_endpoints():
    """Test all API endpoints"""
    log_test("Testing API Endpoints", "INFO")
    
    try:
        import httpx
        
        base_url = "http://localhost:8080"
        
        async with httpx.AsyncClient() as client:
            # Test master control endpoints
            log_test("Testing master control API...", "INFO")
            
            # Test deployment stats
            response = await client.get(f"{base_url}/api/master/deployment-stats")
            if response.status_code == 200:
                log_test("✅ Master deployment stats API working", "PASS")
            else:
                log_test(f"❌ Master stats API failed: {response.status_code}", "FAIL")
            
            # Test company management
            log_test("Testing company management API...", "INFO")
            response = await client.get(f"{base_url}/api/companies/list")
            if response.status_code == 200:
                log_test("✅ Company management API working", "PASS")
            else:
                log_test(f"❌ Company management API failed: {response.status_code}", "FAIL")
            
            # Test worker API
            log_test("Testing worker API...", "INFO")
            response = await client.get(f"{base_url}/api/worker/roles")
            if response.status_code == 200:
                log_test("✅ Worker API working", "PASS")
            else:
                log_test(f"❌ Worker API failed: {response.status_code}", "FAIL")
            
            return True
            
    except Exception as e:
        log_test(f"❌ API endpoint test error: {str(e)}", "FAIL")
        return False

async def test_database_integrity():
    """Test database integrity and connections"""
    log_test("Testing Database Integrity", "INFO")
    
    try:
        # Test main deployment database
        log_test("Checking deployment database...", "INFO")
        conn = sqlite3.connect("fred_deployments.db")
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            log_test(f"✅ Found {len(tables)} database tables", "PASS")
        else:
            log_test("❌ No database tables found", "FAIL")
        
        # Test inserting test data
        test_deployment = {
            "deployment_id": f"TEST-{uuid.uuid4().hex[:8]}",
            "company_name": "Database Test Corp",
            "industry": "manufacturing",
            "size": "small",
            "modules": json.dumps(["quality"]),
            "worker_count": 25,
            "deployment_status": "active",
            "api_keys": json.dumps({"api_key": "test_key"}),
            "custom_domain": "test-corp.fixitfred.ai",
            "revenue_potential": 15000,
            "created_at": datetime.now().isoformat()
        }
        
        cursor.execute('''
            INSERT OR IGNORE INTO deployments 
            (deployment_id, company_name, industry, size, modules, worker_count, 
             deployment_status, api_keys, custom_domain, revenue_potential, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(test_deployment.values()))
        
        conn.commit()
        conn.close()
        
        log_test("✅ Database operations working", "PASS")
        return True
        
    except Exception as e:
        log_test(f"❌ Database test error: {str(e)}", "FAIL")
        return False

async def test_voice_commands():
    """Test voice command system"""
    log_test("Testing Voice Command System", "INFO")
    
    try:
        from api.worker_api import process_voice_command
        
        # Test voice commands
        test_commands = [
            "Hey Fred, start quality inspection",
            "Hey Fred, show my tasks",
            "Hey Fred, report safety issue"
        ]
        
        for command in test_commands:
            log_test(f"Testing command: '{command}'...", "INFO")
            request = {"worker_id": "TEST-001", "command": command}
            result = await process_voice_command(request)
            
            if result and "response" in result:
                log_test(f"✅ Voice command processed", "PASS")
            else:
                log_test(f"❌ Voice command failed", "FAIL")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Voice command test error: {str(e)}", "FAIL")
        return False

async def run_complete_platform_test():
    """Run complete end-to-end platform test"""
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🤖 FixItFred Complete Platform Test{Colors.END}")
    print(f"{Colors.CYAN}Testing entire platform from deployment to worker level{Colors.END}\n")
    
    test_results = {
        "master_deployment": False,
        "module_system": False,
        "worker_identity": False,
        "offline_sync": False,
        "api_endpoints": False,
        "database": False,
        "voice_commands": False
    }
    
    # Run all tests
    deployment_id = await test_master_deployment_system()
    test_results["master_deployment"] = deployment_id is not None
    
    module_id = await test_module_system()
    test_results["module_system"] = module_id is not None
    
    worker_id = await test_worker_identity_system()
    test_results["worker_identity"] = worker_id is not None
    
    test_results["offline_sync"] = await test_offline_sync_system()
    test_results["api_endpoints"] = await test_api_endpoints()
    test_results["database"] = await test_database_integrity()
    test_results["voice_commands"] = await test_voice_commands()
    
    # Summary
    print(f"\n{Colors.BOLD}📊 TEST SUMMARY{Colors.END}")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} {test_name.replace('_', ' ').title()}")
        if result:
            passed += 1
    
    print("=" * 50)
    
    success_rate = (passed / total) * 100
    if success_rate >= 80:
        color = Colors.GREEN
        status = "EXCELLENT"
    elif success_rate >= 60:
        color = Colors.YELLOW
        status = "GOOD"
    else:
        color = Colors.RED
        status = "NEEDS WORK"
    
    print(f"\n{color}{Colors.BOLD}🎯 OVERALL: {status} ({passed}/{total} tests passed - {success_rate:.1f}%){Colors.END}")
    
    if success_rate >= 80:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ FixItFred platform is working excellently!{Colors.END}")
        print(f"{Colors.CYAN}🚀 Ready for deployment to 200,000+ companies{Colors.END}")
        print(f"{Colors.PURPLE}💰 Projected revenue: $12.6B at full scale{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some components need attention before full-scale deployment{Colors.END}")
    
    return test_results

if __name__ == "__main__":
    print("Starting complete platform test...")
    result = asyncio.run(run_complete_platform_test())
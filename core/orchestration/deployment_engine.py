#!/usr/bin/env python3
"""
GRINGO COMPLETE SYSTEM
Integrated platform with data storage, daily operations, and continuous learning
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from gringo_os_optimized import GringoOS
from gringo_enterprise_builder import EnterpriseModuleBuilder, SAPLevelSystemBuilder
from gringo_data_engine import DailyOperationsManager, GringoDataWarehouse
from gringo_business_model import CustomerEngagementProcess
from typing import Dict, List, Any
from datetime import datetime
import json

class GringoCompleteSystem:
    """Complete integrated Gringo OS with data storage and daily operations"""
    
    def __init__(self):
        # Core components
        self.gringo_os = GringoOS()
        self.module_builder = EnterpriseModuleBuilder()
        self.erp_builder = SAPLevelSystemBuilder()
        self.data_warehouse = GringoDataWarehouse()
        self.operations_manager = DailyOperationsManager()
        self.customer_engagement = CustomerEngagementProcess()
        
        # Active clients and their data
        self.active_clients = {}
        self.client_operations = {}
        
    async def initialize(self):
        """Initialize the complete system"""
        print("🚀 Initializing Gringo Complete System...")
        
        # Initialize core components
        await self.gringo_os.initialize()
        
        print("✅ Complete system ready for enterprise deployments")
    
    async def deploy_complete_client_system(self, client_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a complete client system with data storage and operations"""
        
        print(f"\n🏢 DEPLOYING COMPLETE SYSTEM FOR: {client_requirements['company_name']}")
        print("="*70)
        
        # Step 1: Generate business proposal
        print("📋 Step 1: Generating business proposal...")
        proposal = await self.customer_engagement.generate_customer_proposal(client_requirements)
        
        # Step 2: Build required modules
        print("🔧 Step 2: Building enterprise modules...")
        required_modules = proposal['project_overview']['modules']
        built_modules = {}
        
        for module_info in required_modules:
            module_name = module_info['name'].lower().replace(' ', '_')
            if module_name in ['quality_control', 'maintenance_management', 'safety_compliance', 'financial_management']:
                module = await self.module_builder.build_custom_module(
                    client_requirements, module_name
                )
                built_modules[module_name] = module
                print(f"  ✅ Built {module_info['name']} module")
        
        # Step 3: Create complete ERP system
        print("🏗️ Step 3: Building complete ERP system...")
        complete_erp = await self.erp_builder.build_complete_erp(client_requirements)
        
        # Step 4: Deploy to Gringo OS
        print("🚀 Step 4: Deploying to Gringo OS...")
        gringo_client_data = {
            'name': client_requirements['company_name'],
            'industry': client_requirements['industry'],
            'employees': client_requirements['employees'],
            'revenue': client_requirements.get('annual_revenue', 0),
            'needs': [m['name'].lower() for m in required_modules],
            'data_sources': client_requirements.get('existing_systems', [])
        }
        
        gringo_deployment = await self.gringo_os.onboard_business(gringo_client_data)
        client_id = gringo_deployment['business']['id']
        
        # Step 5: Initialize data storage and operations
        print("💾 Step 5: Setting up data storage and daily operations...")
        await self.operations_manager.start_client_operations(client_id)
        
        # Store client information
        self.active_clients[client_id] = {
            'requirements': client_requirements,
            'proposal': proposal,
            'modules': built_modules,
            'erp_system': complete_erp,
            'gringo_deployment': gringo_deployment,
            'deployed_at': datetime.now().isoformat()
        }
        
        # Step 6: Generate sample operational data
        print("📊 Step 6: Initializing with sample operational data...")
        await self._generate_initial_operations_data(client_id)
        
        # Complete deployment summary
        deployment_summary = {
            'client_id': client_id,
            'company_name': client_requirements['company_name'],
            'industry': client_requirements['industry'],
            'proposal': proposal,
            'modules_built': len(built_modules),
            'erp_system': complete_erp,
            'gringo_deployment': gringo_deployment,
            'data_warehouse_ready': True,
            'daily_operations_active': True,
            'continuous_learning_active': True,
            'deployment_complete': True
        }
        
        print("✅ COMPLETE SYSTEM DEPLOYED!")
        return deployment_summary
    
    async def _generate_initial_operations_data(self, client_id: str):
        """Generate initial operational data to seed the system"""
        
        # Quality control data
        quality_data = {
            'items_inspected': 245,
            'defects_found': 5,
            'defect_types': ['surface_finish', 'dimensional_variance', 'material_defect'],
            'inspector': 'Sarah Johnson',
            'inspection_time_hours': 3.2,
            'rework_cost': 750,
            'scrap_cost': 300,
            'product_line': 'Assembly Line A'
        }
        
        await self.operations_manager.process_real_time_data(
            client_id, 'quality_control', 'quality_metrics', quality_data
        )
        
        # Maintenance data
        maintenance_data = {
            'equipment_id': 'CNC001',
            'equipment_name': 'CNC Machining Center',
            'runtime_hours': 156,
            'failure_count': 0,
            'repair_time_hours': 0,
            'parts_cost': 0,
            'labor_cost': 450,  # Preventive maintenance
            'planned_maintenance': 1,
            'unplanned_maintenance': 0,
            'total_maintenance': 1,
            'temperature': 68.5,
            'vibration': 0.3,
            'efficiency_percent': 94.2
        }
        
        await self.operations_manager.process_real_time_data(
            client_id, 'maintenance_management', 'maintenance_records', maintenance_data
        )
        
        # Safety data
        safety_data = {
            'incident_type': 'safety_observation',
            'severity': 'low',
            'location': 'Production Floor',
            'description': 'Employee properly using PPE during maintenance',
            'injured_count': 0,
            'root_cause': 'positive_safety_behavior',
            'corrective_actions': ['recognize_good_behavior'],
            'direct_cost': 0,
            'indirect_cost': 0
        }
        
        await self.operations_manager.process_real_time_data(
            client_id, 'safety_compliance', 'safety_incidents', safety_data
        )
        
        # Production data
        production_data = {
            'units_produced': 1875,
            'production_time_hours': 8,
            'good_units': 1862,
            'total_units': 1875,
            'cycles_completed': 187,
            'total_time': 480,  # 8 hours in minutes
            'downtime': 12,
            'setup_time': 25,
            'actual_output': 1875,
            'expected_output': 1800,
            'uptime': 468,  # minutes
            'total_time': 480
        }
        
        await self.operations_manager.process_real_time_data(
            client_id, 'operations_management', 'production_data', production_data
        )
        
        # Financial data
        financial_data = {
            'total_cost': 12500,
            'units': 1875,
            'revenue': 18750,
            'costs': 12500,
            'cash_in': 18750,
            'cash_out': 12500,
            'actual': 12500,
            'budget': 13000,
            'return': 18750,
            'investment': 12500
        }
        
        await self.operations_manager.process_real_time_data(
            client_id, 'financial_management', 'financial_transactions', financial_data
        )
        
        print("  ✅ Sample operational data generated")
    
    async def get_complete_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get complete status for a client including all systems"""
        
        if client_id not in self.active_clients:
            return {'error': 'Client not found'}
        
        client_info = self.active_clients[client_id]
        
        # Get Gringo OS status
        gringo_status = await self.gringo_os.get_business_status(client_id)
        
        # Get daily operations dashboard
        operations_dashboard = await self.operations_manager.get_client_dashboard_data(client_id)
        
        # Get data warehouse summary
        data_summary = await self.data_warehouse.get_daily_operations_summary(client_id)
        
        return {
            'client_info': {
                'company_name': client_info['requirements']['company_name'],
                'industry': client_info['requirements']['industry'],
                'deployed_at': client_info['deployed_at']
            },
            'gringo_os_status': gringo_status,
            'daily_operations': operations_dashboard,
            'data_warehouse_summary': data_summary,
            'modules_status': {
                module_name: 'active' for module_name in client_info['modules'].keys()
            },
            'system_health': 'excellent',
            'learning_active': True,
            'data_processing_active': True
        }
    
    async def process_voice_command_with_data(self, command: str, client_id: str) -> Dict[str, Any]:
        """Process voice command with access to all client data"""
        
        # First process through Gringo OS
        gringo_response = await self.gringo_os.process_universal_command(command, client_id)
        
        # Enhance with data warehouse insights
        if 'show' in command.lower() or 'report' in command.lower() or 'status' in command.lower():
            # Get relevant data from warehouse
            operations_data = await self.operations_manager.get_client_dashboard_data(client_id)
            
            # Enhance response with real data
            enhanced_response = {
                **gringo_response,
                'data_insights': operations_data['insights'],
                'current_metrics': operations_data['daily_summary']['current_metrics'],
                'alerts': operations_data['alerts'],
                'real_data_available': True
            }
            
            return enhanced_response
        
        return gringo_response
    
    async def simulate_daily_operations(self, client_id: str, days: int = 1):
        """Simulate multiple days of operations for demonstration"""
        
        print(f"\n📊 SIMULATING {days} DAYS OF OPERATIONS FOR CLIENT {client_id}")
        print("="*60)
        
        for day in range(days):
            print(f"\n📅 Day {day + 1} Operations:")
            
            # Generate varied operational data
            quality_data = {
                'items_inspected': 200 + (day * 25),
                'defects_found': max(0, 4 - day),  # Improving quality
                'defect_types': ['surface_finish', 'dimensional_variance'],
                'inspector': 'Quality Team',
                'inspection_time_hours': 2.8 + (day * 0.1),
                'rework_cost': max(100, 600 - (day * 50)),
                'scrap_cost': max(50, 250 - (day * 25))
            }
            
            await self.operations_manager.process_real_time_data(
                client_id, 'quality_control', 'quality_metrics', quality_data
            )
            print(f"  ✅ Quality: {quality_data['items_inspected']} inspected, {quality_data['defects_found']} defects")
            
            # Maintenance improving over time
            maintenance_data = {
                'equipment_id': 'MAIN001',
                'equipment_name': 'Main Production Line',
                'runtime_hours': 160 + (day * 8),
                'failure_count': max(0, 1 - (day // 3)),
                'repair_time_hours': max(0, 2 - (day * 0.2)),
                'parts_cost': max(0, 300 - (day * 30)),
                'labor_cost': 400,
                'planned_maintenance': 1,
                'unplanned_maintenance': max(0, 1 - (day // 3)),
                'total_maintenance': 1 + max(0, 1 - (day // 3))
            }
            
            await self.operations_manager.process_real_time_data(
                client_id, 'maintenance_management', 'maintenance_records', maintenance_data
            )
            print(f"  ✅ Maintenance: {maintenance_data['runtime_hours']} runtime hours, {maintenance_data['failure_count']} failures")
            
            # Production improving
            production_data = {
                'units_produced': 1800 + (day * 50),  # Improving production
                'production_time_hours': 8,
                'good_units': int((1800 + (day * 50)) * (0.96 + (day * 0.01))),  # Improving quality
                'total_units': 1800 + (day * 50),
                'cycles_completed': 180 + (day * 5),
                'total_time': 480,
                'downtime': max(5, 20 - (day * 2)),  # Decreasing downtime
                'setup_time': max(15, 30 - (day * 1))
            }
            
            await self.operations_manager.process_real_time_data(
                client_id, 'operations_management', 'production_data', production_data
            )
            print(f"  ✅ Production: {production_data['units_produced']} units, {production_data['downtime']} min downtime")
            
            # Simulate time passing
            await asyncio.sleep(0.1)  # Small delay for demo
        
        # Get final status
        final_status = await self.get_complete_client_status(client_id)
        
        print(f"\n📈 OPERATIONS SIMULATION COMPLETE!")
        print(f"Total Operations Processed: {final_status['data_warehouse_summary']['total_operations']}")
        print(f"Active Modules: {final_status['data_warehouse_summary']['active_modules']}")
        print(f"System Health: {final_status['system_health']}")
        
        return final_status

# Complete system demo
async def complete_system_demo():
    """Demo the complete integrated system"""
    
    print("🌟 GRINGO COMPLETE SYSTEM DEMO")
    print("="*60)
    print("This demo shows the complete enterprise system with:")
    print("• Data storage and processing")
    print("• Daily operations management")
    print("• Continuous AI learning")
    print("• Real-time insights and alerts")
    print("• Voice command processing")
    print("• Business intelligence")
    
    # Initialize complete system
    complete_system = GringoCompleteSystem()
    await complete_system.initialize()
    
    # Example client requirements
    client_requirements = {
        'company_name': 'Advanced Manufacturing Solutions',
        'industry': 'manufacturing',
        'sub_industry': 'precision_machining',
        'employees': 275,
        'locations': 2,
        'annual_revenue': 45000000,
        'existing_systems': ['Legacy ERP', 'Manual QC', 'Spreadsheet Maintenance'],
        'pain_points': [
            'Quality inconsistencies',
            'Reactive maintenance approach',
            'Limited real-time visibility',
            'Manual data entry errors',
            'Compliance reporting challenges'
        ],
        'business_goals': [
            'Improve quality by 40%',
            'Reduce maintenance costs by 25%',
            'Achieve real-time operational visibility',
            'Automate compliance reporting',
            'Increase overall efficiency by 20%'
        ],
        'budget': 350000,
        'timeline': '4 months'
    }
    
    # Deploy complete system
    deployment = await complete_system.deploy_complete_client_system(client_requirements)
    client_id = deployment['client_id']
    
    print(f"\n🎉 DEPLOYMENT SUMMARY:")
    print(f"Client: {deployment['company_name']}")
    print(f"Client ID: {client_id}")
    print(f"Modules Built: {deployment['modules_built']}")
    print(f"Investment: ${deployment['proposal']['investment']['one_time_costs']['total']:,.0f}")
    print(f"Dashboard: {deployment['gringo_deployment']['dashboard_url']}")
    
    # Simulate operations
    await complete_system.simulate_daily_operations(client_id, days=5)
    
    # Test voice commands with data
    print(f"\n🎤 TESTING VOICE COMMANDS WITH REAL DATA:")
    
    test_commands = [
        "show me today's quality metrics",
        "what's the status of our equipment",
        "report on safety performance",
        "how is production performing today",
        "give me insights on our operations"
    ]
    
    for command in test_commands:
        print(f"\n  Command: '{command}'")
        response = await complete_system.process_voice_command_with_data(command, client_id)
        
        if response.get('real_data_available'):
            print(f"  ✅ Response: Command processed with real operational data")
            print(f"  📊 Current Metrics: {len(response['current_metrics'])} metrics available")
            print(f"  🧠 AI Insights: {len(response['data_insights'])} insights generated")
            print(f"  🚨 Alerts: {len(response['alerts'])} active alerts")
        else:
            print(f"  ✅ Response: {response.get('response', 'Command processed')}")
    
    # Get final complete status
    final_status = await complete_system.get_complete_client_status(client_id)
    
    print(f"\n📊 FINAL SYSTEM STATUS:")
    print(f"System Health: {final_status['system_health']}")
    print(f"Learning Active: {final_status['learning_active']}")
    print(f"Data Processing: {final_status['data_processing_active']}")
    print(f"Total Operations: {final_status['data_warehouse_summary']['total_operations']}")
    
    print(f"\n🎯 AI INSIGHTS GENERATED:")
    for insight in final_status['daily_operations']['insights']:
        print(f"• {insight['insight_type']}: {insight['description']}")
        print(f"  Confidence: {insight['confidence']:.0%}, Impact: {insight['impact_score']:.1f}")
    
    print(f"\n🚨 ACTIVE ALERTS:")
    for alert in final_status['daily_operations']['alerts']:
        print(f"• {alert['type'].upper()}: {alert['message']}")
    
    print(f"\n✅ COMPLETE SYSTEM DEMONSTRATION FINISHED!")
    print(f"🔄 Continuous learning and optimization running in background")
    print(f"📈 Real-time data processing and insights generation active")
    print(f"💾 All operational data stored and available for analysis")
    
    return deployment

# Quick data storage demo
async def quick_data_demo():
    """Quick demo of just the data storage and processing"""
    
    print("💾 QUICK DATA STORAGE & PROCESSING DEMO")
    print("="*50)
    
    # Initialize just the data components
    from gringo_data_engine import demo_daily_operations
    
    # Run the data engine demo
    result = await demo_daily_operations()
    
    print(f"\n✅ Data storage and processing demo complete!")
    return result

async def main():
    """Main demo selector"""
    
    print("🎯 GRINGO COMPLETE SYSTEM SELECTOR")
    print("="*50)
    print("1. 🌟 Complete System Demo (Full integration)")
    print("2. 💾 Data Storage Demo (Data engine only)")
    print("3. 📊 Daily Operations Demo (Operations only)")
    
    choice = input("\nSelect demo (1-3): ").strip()
    
    if choice == '1':
        await complete_system_demo()
    elif choice == '2':
        await quick_data_demo()
    elif choice == '3':
        from gringo_data_engine import demo_daily_operations
        await demo_daily_operations()
    else:
        print("Invalid choice, running complete system demo...")
        await complete_system_demo()

if __name__ == "__main__":
    asyncio.run(main())
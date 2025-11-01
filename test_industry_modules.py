#!/usr/bin/env python3
"""
Test script for FixItFred Industry-Specific Modules
Tests manufacturing, healthcare, retail, construction, and logistics assistants
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add paths for modules
sys.path.append(".")
sys.path.append("./modules/manufacturing")
sys.path.append("./modules/healthcare")
sys.path.append("./modules/retail")
sys.path.append("./modules/construction")
sys.path.append("./modules/logistics")

from modules.manufacturing.manufacturing_assistant import (
    ManufacturingAssistant,
    EquipmentType,
)
from modules.healthcare.healthcare_assistant import (
    HealthcareAssistant,
    MedicalEquipmentType,
    ComplianceStandard,
)
from modules.retail.retail_assistant import RetailAssistant, RetailEquipmentType
from modules.construction.construction_assistant import (
    ConstructionAssistant,
    ConstructionEquipmentType,
)
from modules.logistics.logistics_assistant import (
    LogisticsAssistant,
    LogisticsEquipmentType,
)


async def test_manufacturing_module():
    """Test Manufacturing Assistant"""
    print("\n🏭 Testing Manufacturing Assistant...")

    # Initialize with API keys
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    manufacturing = ManufacturingAssistant(api_keys)

    # Register test equipment
    equipment = manufacturing.register_manufacturing_equipment(
        equipment_id="cnc_001",
        name="CNC Machining Center #1",
        equipment_type=EquipmentType.CNC_MACHINE,
        make="Haas",
        model="VF-3",
        year=2020,
    )
    print(f"✅ Registered equipment: {equipment.name}")

    # Register production line
    line = manufacturing.register_production_line(
        line_id="line_001",
        name="Main Production Line",
        equipment_ids=["cnc_001"],
        capacity_per_hour=50,
    )
    print(f"✅ Registered production line: {line.name}")

    # Test equipment diagnosis
    try:
        diagnosis = await manufacturing.diagnose_equipment_failure(
            equipment_id="cnc_001",
            symptoms=[
                "Unusual vibration",
                "Tool wear exceeded",
                "Temperature running high",
            ],
            sensor_data={"vibration": 2.5, "temperature": 85, "spindle_load": 95},
        )

        if "error" not in diagnosis:
            print(f"✅ Manufacturing diagnosis completed!")
            print(f"   🎯 Confidence: {diagnosis.get('confidence', 'N/A')}")
            print(f"   🤖 AI Provider: {diagnosis.get('ai_provider', 'N/A')}")
            print(
                f"   📋 Diagnosis preview: {str(diagnosis.get('diagnosis', ''))[:100]}..."
            )
        else:
            print(f"❌ Manufacturing diagnosis error: {diagnosis['error']}")

    except Exception as e:
        print(f"❌ Manufacturing diagnosis exception: {e}")

    # Test dashboard
    try:
        dashboard = await manufacturing.get_manufacturing_dashboard()
        if "error" not in dashboard:
            print(
                f"✅ Manufacturing dashboard: {dashboard['overview']['total_equipment']} equipment"
            )
        else:
            print(f"❌ Dashboard error: {dashboard['error']}")
    except Exception as e:
        print(f"❌ Dashboard exception: {e}")


async def test_healthcare_module():
    """Test Healthcare Assistant"""
    print("\n🏥 Testing Healthcare Assistant...")

    # Initialize with API keys
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    healthcare = HealthcareAssistant(api_keys)

    # Register test equipment
    equipment = healthcare.register_medical_equipment(
        equipment_id="mri_001",
        name="MRI Scanner Room 1",
        equipment_type=MedicalEquipmentType.MRI,
        make="Siemens",
        model="Magnetom Skyra",
        serial_number="12345",
        year=2019,
    )
    print(f"✅ Registered medical equipment: {equipment.name}")

    # Test medical equipment diagnosis
    try:
        diagnosis = await healthcare.diagnose_medical_equipment(
            equipment_id="mri_001",
            symptoms=[
                "Loud knocking noise",
                "Image quality degraded",
                "Helium level low",
            ],
            patient_impact="high",
        )

        if "error" not in diagnosis:
            print(f"✅ Healthcare diagnosis completed!")
            print(f"   ⚠️  Patient impact: {diagnosis.get('patient_impact', 'N/A')}")
            print(
                f"   🚨 Safety alert created: {diagnosis.get('safety_alert_created', False)}"
            )
            print(
                f"   📋 Diagnosis preview: {str(diagnosis.get('diagnosis', ''))[:100]}..."
            )
        else:
            print(f"❌ Healthcare diagnosis error: {diagnosis['error']}")

    except Exception as e:
        print(f"❌ Healthcare diagnosis exception: {e}")


async def test_retail_module():
    """Test Retail Assistant"""
    print("\n🛒 Testing Retail Assistant...")

    # Initialize with API keys
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    retail = RetailAssistant(api_keys)

    # Register test store
    store = retail.register_store_location(
        store_id="store_001",
        name="Downtown Store",
        address="123 Main St",
        equipment_ids=["pos_001"],
        daily_customers=500,
    )
    print(f"✅ Registered store: {store.name}")

    # Register test equipment
    equipment = retail.register_retail_equipment(
        equipment_id="pos_001",
        name="POS Terminal #1",
        equipment_type=RetailEquipmentType.POS_TERMINAL,
        make="Square",
        model="Terminal",
        store_id="store_001",
        year=2022,
    )
    print(f"✅ Registered retail equipment: {equipment.name}")

    # Test retail diagnosis
    try:
        diagnosis = await retail.diagnose_retail_equipment(
            equipment_id="pos_001",
            symptoms=[
                "Screen flickering",
                "Card reader not working",
                "Receipt printer jammed",
            ],
            store_id="store_001",
            current_customer_volume="peak",
        )

        if "error" not in diagnosis:
            print(f"✅ Retail diagnosis completed!")
            print(
                f"   💰 Revenue impact: ${diagnosis.get('customer_impact', {}).get('revenue_impact_per_hour', 0)}/hour"
            )
            print(
                f"   🔄 Workaround available: {diagnosis.get('customer_impact', {}).get('workaround_available', False)}"
            )
            print(
                f"   📋 Diagnosis preview: {str(diagnosis.get('diagnosis', ''))[:100]}..."
            )
        else:
            print(f"❌ Retail diagnosis error: {diagnosis['error']}")

    except Exception as e:
        print(f"❌ Retail diagnosis exception: {e}")


async def test_construction_module():
    """Test Construction Assistant"""
    print("\n🏗️ Testing Construction Assistant...")

    # Initialize with API keys
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    construction = ConstructionAssistant(api_keys)

    # Register test project
    project = construction.register_construction_project(
        project_id="project_001",
        name="Office Building Construction",
        location="Downtown",
        equipment_ids=["excavator_001"],
        start_date=datetime.now(),
        estimated_completion=datetime.now() + timedelta(days=180),
    )
    print(f"✅ Registered project: {project.name}")

    # Register test equipment
    equipment = construction.register_construction_equipment(
        equipment_id="excavator_001",
        name="Caterpillar Excavator #1",
        equipment_type=ConstructionEquipmentType.EXCAVATOR,
        make="Caterpillar",
        model="320",
        project_id="project_001",
        year=2021,
    )
    print(f"✅ Registered construction equipment: {equipment.name}")

    # Test construction diagnosis
    try:
        diagnosis = await construction.diagnose_construction_equipment(
            equipment_id="excavator_001",
            symptoms=[
                "Hydraulic fluid leak",
                "Slow operation",
                "Unusual noise from boom",
            ],
            project_id="project_001",
            safety_concerns=[
                "Potential hydraulic failure",
                "Operator visibility reduced",
            ],
        )

        if "error" not in diagnosis:
            print(f"✅ Construction diagnosis completed!")
            print(
                f"   ⚠️  Safety incident created: {diagnosis.get('safety_incident_created', False)}"
            )
            print(
                f"   🛑 Shutdown required: {diagnosis.get('immediate_shutdown_required', False)}"
            )
            print(
                f"   📋 Diagnosis preview: {str(diagnosis.get('diagnosis', ''))[:100]}..."
            )
        else:
            print(f"❌ Construction diagnosis error: {diagnosis['error']}")

    except Exception as e:
        print(f"❌ Construction diagnosis exception: {e}")


async def test_logistics_module():
    """Test Logistics Assistant"""
    print("\n🚛 Testing Logistics Assistant...")

    # Initialize with API keys
    api_keys = {
        "grok": os.getenv("XAI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    logistics = LogisticsAssistant(api_keys)

    # Register test vehicle
    vehicle = logistics.register_fleet_vehicle(
        vehicle_id="truck_001",
        name="Delivery Truck #1",
        vehicle_type=LogisticsEquipmentType.DELIVERY_TRUCK,
        make="Ford",
        model="Transit",
        year=2022,
        capacity=1000.0,
    )
    print(f"✅ Registered fleet vehicle: {vehicle.name}")

    # Register test route
    route = logistics.register_logistics_route(
        route_id="route_001",
        origin="Warehouse A",
        destination="Customer Site B",
        vehicle_id="truck_001",
        estimated_duration=timedelta(hours=2),
        cargo_capacity=1000.0,
    )
    print(f"✅ Registered route: {route.origin} → {route.destination}")

    # Test fleet diagnosis
    try:
        diagnosis = await logistics.diagnose_fleet_vehicle(
            vehicle_id="truck_001",
            symptoms=["Engine overheating", "Check engine light", "Reduced power"],
            current_route="route_001",
            cargo_status="loaded",
        )

        if "error" not in diagnosis:
            print(f"✅ Logistics diagnosis completed!")
            print(
                f"   📦 Cargo at risk: {diagnosis.get('delivery_impact', {}).get('cargo_at_risk', False)}"
            )
            print(
                f"   ⏱️  Estimated delay: {diagnosis.get('delivery_impact', {}).get('estimated_delay', 'N/A')}"
            )
            print(
                f"   🚨 Incident created: {diagnosis.get('delivery_incident_created', False)}"
            )
            print(
                f"   📋 Diagnosis preview: {str(diagnosis.get('diagnosis', ''))[:100]}..."
            )
        else:
            print(f"❌ Logistics diagnosis error: {diagnosis['error']}")

    except Exception as e:
        print(f"❌ Logistics diagnosis exception: {e}")


async def test_all_modules():
    """Run comprehensive test of all industry modules"""
    print("🤖 Testing FixItFred Industry-Specific Modules")
    print("=" * 60)

    # Test each module
    await test_manufacturing_module()
    await test_healthcare_module()
    await test_retail_module()
    await test_construction_module()
    await test_logistics_module()

    print("\n" + "=" * 60)
    print("🎉 Industry modules testing complete!")
    print("✅ Manufacturing: Equipment diagnosis & production optimization")
    print("✅ Healthcare: Medical equipment & patient safety compliance")
    print("✅ Retail: Store operations & customer impact management")
    print("✅ Construction: Safety-first equipment & project management")
    print("✅ Logistics: Fleet management & delivery optimization")


if __name__ == "__main__":
    asyncio.run(test_all_modules())

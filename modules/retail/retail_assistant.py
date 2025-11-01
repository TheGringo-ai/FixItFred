#!/usr/bin/env python3
"""
FixItFred Retail Assistant Module
AI-powered retail equipment and operations management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Import core FixItFred
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.ai_brain.fix_it_fred_core import (
    FixItFredCore,
    Asset,
    MaintenanceTask,
    TaskPriority,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class RetailEquipmentType(Enum):
    """Retail equipment types"""

    POS_TERMINAL = "pos_terminal"
    CASH_REGISTER = "cash_register"
    BARCODE_SCANNER = "barcode_scanner"
    RECEIPT_PRINTER = "receipt_printer"
    SECURITY_CAMERA = "security_camera"
    REFRIGERATION = "refrigeration_unit"
    FREEZER = "freezer"
    HVAC_RETAIL = "hvac_retail"
    DISPLAY_SCREEN = "display_screen"
    SHOPPING_CART = "shopping_cart"
    CONVEYOR_BELT = "conveyor_belt"
    SCALE = "electronic_scale"


class StoreOperationType(Enum):
    """Store operation types"""

    CHECKOUT = "checkout_operations"
    INVENTORY = "inventory_management"
    SECURITY = "security_systems"
    CLIMATE = "climate_control"
    LIGHTING = "lighting_systems"
    CUSTOMER_SERVICE = "customer_service"


@dataclass
class StoreLocation:
    """Store location configuration"""

    store_id: str
    name: str
    address: str
    equipment_ids: List[str]
    daily_customers: int
    operating_hours: str = "9AM-9PM"
    store_type: str = "retail"


@dataclass
class CustomerImpactAssessment:
    """Customer experience impact assessment"""

    impact_id: str
    equipment_id: str
    impact_level: str  # critical, high, medium, low
    affected_operations: List[str]
    customer_count_affected: int
    revenue_impact_per_hour: float
    workaround_available: bool


class RetailAssistant(FixItFredCore):
    """
    Retail-specific AI assistant
    Extends FixItFred with retail operations expertise
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)

        # Retail-specific data
        self.store_locations: Dict[str, StoreLocation] = {}
        self.customer_impact_assessments: Dict[str, CustomerImpactAssessment] = {}
        self.peak_hours: Dict[str, List[str]] = {}

        logger.info("🛒 Retail Assistant initialized")

    async def diagnose_retail_equipment(
        self,
        equipment_id: str,
        symptoms: List[str],
        store_id: str,
        current_customer_volume: str = "normal",
    ) -> Dict[str, Any]:
        """
        Diagnose retail equipment with customer impact focus
        """
        equipment = self.assets.get(equipment_id)
        if not equipment:
            return {"error": "Retail equipment not found"}

        store = self.store_locations.get(store_id)
        store_context = f"Store: {store.name}" if store else "Store: Unknown"

        prompt = f"""RETAIL EQUIPMENT DIAGNOSIS:

Equipment: {equipment.name} ({equipment.make} {equipment.model})
Type: {equipment.asset_type}
{store_context}
Symptoms: {', '.join(symptoms)}
Current Customer Volume: {current_customer_volume}

As a retail operations specialist, provide:

1. CUSTOMER IMPACT ASSESSMENT
   - Immediate customer experience effects
   - Checkout delays and bottlenecks
   - Sales revenue impact per hour
   - Customer satisfaction implications

2. OPERATIONAL DIAGNOSIS
   - Equipment failure analysis
   - POS system connectivity issues
   - Network and software problems
   - Hardware component failures

3. BUSINESS CONTINUITY
   - Immediate workaround solutions
   - Backup equipment deployment
   - Staff redeployment strategies
   - Customer communication protocols

4. REPAIR STRATEGY
   - On-site vs remote diagnosis
   - Vendor support requirements
   - Parts availability and lead times
   - Repair window optimization

5. PREVENTION MEASURES
   - Proactive monitoring setup
   - Preventive maintenance schedules
   - Staff training improvements
   - Equipment lifecycle planning

6. COST-BENEFIT ANALYSIS
   - Repair costs vs replacement
   - Lost revenue calculations
   - Customer retention impact
   - Long-term investment planning

Prioritize minimizing customer disruption and revenue loss."""

        try:
            if self.ai_team:
                responses = await self.ai_team.diagnose_with_ai_team(
                    prompt,
                    {
                        "equipment_type": equipment.asset_type,
                        "store_context": store_context,
                    },
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Assess customer impact
                impact_level = (
                    "high" if current_customer_volume in ["peak", "high"] else "medium"
                )
                if equipment.asset_type in ["pos_terminal", "cash_register"]:
                    impact_level = "critical"

                impact_assessment = CustomerImpactAssessment(
                    impact_id=f"impact_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    equipment_id=equipment_id,
                    impact_level=impact_level,
                    affected_operations=["checkout_operations"]
                    if "pos" in equipment.asset_type
                    else ["general_operations"],
                    customer_count_affected=100
                    if current_customer_volume == "peak"
                    else 50,
                    revenue_impact_per_hour=500.0
                    if impact_level == "critical"
                    else 200.0,
                    workaround_available=equipment.asset_type
                    not in ["pos_terminal", "cash_register"],
                )
                self.customer_impact_assessments[
                    impact_assessment.impact_id
                ] = impact_assessment

                return {
                    "equipment_id": equipment_id,
                    "store_id": store_id,
                    "diagnosis": best_response.content,
                    "confidence": best_response.confidence,
                    "ai_provider": best_response.provider.value,
                    "repair_instructions": best_response.fix_instructions,
                    "customer_impact": {
                        "level": impact_level,
                        "revenue_impact_per_hour": impact_assessment.revenue_impact_per_hour,
                        "workaround_available": impact_assessment.workaround_available,
                    },
                    "business_continuity_actions": best_response.suggestions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                diagnosis = await self.think(prompt, task_type="retail_diagnosis")
                return {
                    "equipment_id": equipment_id,
                    "store_id": store_id,
                    "diagnosis": diagnosis,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Retail equipment diagnosis error: {e}")
            return {"error": str(e)}

    async def optimize_store_operations(
        self, store_id: str, current_metrics: Dict[str, float], peak_hours: List[str]
    ) -> Dict[str, Any]:
        """
        AI-powered store operations optimization
        """
        store = self.store_locations.get(store_id)
        if not store:
            return {"error": "Store not found"}

        prompt = f"""RETAIL STORE OPERATIONS OPTIMIZATION:

Store: {store.name}
Daily Customers: {store.daily_customers}
Operating Hours: {store.operating_hours}
Peak Hours: {', '.join(peak_hours)}

Current Metrics:
- Customer Wait Time: {current_metrics.get('avg_wait_time', 0):.1f} minutes
- Checkout Efficiency: {current_metrics.get('checkout_efficiency', 0):.1%}
- Equipment Uptime: {current_metrics.get('equipment_uptime', 0):.1%}
- Customer Satisfaction: {current_metrics.get('customer_satisfaction', 0):.1%}
- Revenue per Hour: ${current_metrics.get('revenue_per_hour', 0):.0f}

OPTIMIZATION ANALYSIS:

1. CUSTOMER FLOW OPTIMIZATION
   - Checkout lane management
   - Queue optimization strategies
   - Self-checkout deployment
   - Staff allocation during peaks

2. EQUIPMENT EFFICIENCY
   - POS system optimization
   - Preventive maintenance timing
   - Technology upgrade opportunities
   - Backup system deployment

3. OPERATIONAL IMPROVEMENTS
   - Staff scheduling optimization
   - Inventory management efficiency
   - Customer service enhancements
   - Security system optimization

4. REVENUE ENHANCEMENT
   - Peak hour strategies
   - Equipment reliability improvements
   - Customer experience optimization
   - Upselling opportunity identification

5. COST REDUCTION
   - Energy efficiency improvements
   - Maintenance cost optimization
   - Staff productivity enhancements
   - Technology cost-benefit analysis

6. IMPLEMENTATION ROADMAP
   - Immediate improvements (0-30 days)
   - Short-term projects (1-3 months)
   - Long-term investments (3-12 months)
   - Success metrics and KPIs

Provide actionable recommendations for retail excellence."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="retail_optimization"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Store peak hours for future reference
                self.peak_hours[store_id] = peak_hours

                return {
                    "store_id": store_id,
                    "optimization_plan": best_response.content,
                    "confidence": best_response.confidence,
                    "current_metrics": current_metrics,
                    "peak_hours": peak_hours,
                    "recommended_actions": best_response.suggestions,
                    "implementation_steps": best_response.fix_instructions,
                    "expected_improvements": {
                        "wait_time_reduction": "15-30%",
                        "efficiency_gain": "10-20%",
                        "revenue_increase": "5-15%",
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                optimization = await self.think(prompt, task_type="retail_optimization")
                return {
                    "store_id": store_id,
                    "optimization_plan": optimization,
                    "current_metrics": current_metrics,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Store optimization error: {e}")
            return {"error": str(e)}

    async def create_retail_maintenance_schedule(
        self, store_id: str, equipment_ids: List[str], business_hours: str = "9AM-9PM"
    ) -> Dict[str, Any]:
        """
        Create retail-optimized maintenance schedule
        """
        store = self.store_locations.get(store_id)
        equipment_list = [
            self.assets.get(eid) for eid in equipment_ids if self.assets.get(eid)
        ]

        if not equipment_list:
            return {"error": "No valid equipment found"}

        prompt = f"""RETAIL MAINTENANCE SCHEDULE OPTIMIZATION:

Store: {store.name if store else 'Unknown'}
Business Hours: {business_hours}
Equipment Count: {len(equipment_list)}
Equipment Types: {list(set([e.asset_type for e in equipment_list]))}

CREATE CUSTOMER-FRIENDLY MAINTENANCE SCHEDULE:

1. BUSINESS IMPACT MINIMIZATION
   - Off-hours maintenance priority
   - Peak time avoidance
   - Customer disruption minimization
   - Revenue protection strategies

2. EQUIPMENT PRIORITIZATION
   - Critical systems (POS, payment)
   - Customer-facing equipment
   - Back-of-house systems
   - Security and safety systems

3. PREVENTIVE MAINTENANCE
   - Manufacturer recommendations
   - Usage-based scheduling
   - Seasonal adjustments
   - Technology refresh planning

4. EMERGENCY PREPAREDNESS
   - Backup equipment strategy
   - Rapid response protocols
   - Vendor SLA management
   - Staff training requirements

5. COST OPTIMIZATION
   - Bulk maintenance scheduling
   - Vendor consolidation
   - Warranty management
   - Energy efficiency improvements

6. PERFORMANCE MONITORING
   - KPI tracking systems
   - Customer feedback integration
   - Equipment performance metrics
   - Predictive maintenance indicators

Schedule maintenance to maximize uptime during business hours."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="retail_maintenance"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create maintenance tasks for each equipment
                tasks = []
                for equipment in equipment_list:
                    task = await self.create_task(
                        user_id="retail_system",
                        asset_id=equipment.asset_id,
                        title=f"Retail maintenance - {equipment.name}",
                        description=f"Customer-optimized maintenance for {store.name if store else 'store'}",
                        priority=TaskPriority.MEDIUM,
                    )
                    tasks.append(task)

                return {
                    "store_id": store_id,
                    "maintenance_schedule": best_response.content,
                    "confidence": best_response.confidence,
                    "equipment_count": len(equipment_list),
                    "created_tasks": len(tasks),
                    "business_hours": business_hours,
                    "optimization_focus": "Customer experience and revenue protection",
                    "recommendations": best_response.suggestions,
                    "implementation_plan": best_response.fix_instructions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                schedule = await self.think(prompt, task_type="retail_maintenance")
                return {
                    "store_id": store_id,
                    "maintenance_schedule": schedule,
                    "equipment_count": len(equipment_list),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Retail maintenance schedule error: {e}")
            return {"error": str(e)}

    def register_store_location(
        self,
        store_id: str,
        name: str,
        address: str,
        equipment_ids: List[str],
        daily_customers: int,
    ) -> StoreLocation:
        """Register a new store location"""
        store = StoreLocation(
            store_id=store_id,
            name=name,
            address=address,
            equipment_ids=equipment_ids,
            daily_customers=daily_customers,
        )
        self.store_locations[store_id] = store
        logger.info(f"🛒 Registered store location: {name}")
        return store

    def register_retail_equipment(
        self,
        equipment_id: str,
        name: str,
        equipment_type: RetailEquipmentType,
        make: str,
        model: str,
        store_id: str,
        year: Optional[int] = None,
    ) -> Asset:
        """Register retail equipment"""
        asset = Asset(
            asset_id=equipment_id,
            name=name,
            asset_type=equipment_type.value,
            make=make,
            model=model,
            year=year,
        )
        self.assets[equipment_id] = asset
        logger.info(f"🛒 Registered retail equipment: {name} (Store: {store_id})")
        return asset

    async def get_retail_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive retail dashboard data"""
        try:
            # Get customer impact metrics
            critical_impacts = len(
                [
                    i
                    for i in self.customer_impact_assessments.values()
                    if i.impact_level == "critical"
                ]
            )
            total_revenue_at_risk = sum(
                [
                    i.revenue_impact_per_hour
                    for i in self.customer_impact_assessments.values()
                ]
            )

            # Get equipment status by store
            stores_with_issues = len(
                set([i.equipment_id for i in self.customer_impact_assessments.values()])
            )

            # Get maintenance status
            total_equipment = len(self.assets)
            active_tasks = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
            )

            # Get AI team status if available
            ai_status = {}
            if self.ai_team:
                ai_status = self.ai_team.get_ai_team_status()

            return {
                "customer_impact": {
                    "critical_disruptions": critical_impacts,
                    "revenue_at_risk_per_hour": total_revenue_at_risk,
                    "stores_affected": stores_with_issues,
                },
                "operations": {
                    "total_stores": len(self.store_locations),
                    "total_equipment": total_equipment,
                    "active_maintenance": active_tasks,
                    "equipment_types": list(
                        set([a.asset_type for a in self.assets.values()])
                    ),
                },
                "ai_team_status": ai_status,
                "store_locations": list(self.store_locations.keys()),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Retail dashboard error: {e}")
            return {"error": str(e)}


# Global retail assistant instance
retail_assistant = RetailAssistant()

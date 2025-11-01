#!/usr/bin/env python3
"""
FixItFred Logistics Assistant Module
AI-powered transportation and logistics management
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


class LogisticsEquipmentType(Enum):
    """Logistics equipment types"""

    DELIVERY_TRUCK = "delivery_truck"
    CARGO_VAN = "cargo_van"
    FORKLIFT = "forklift"
    PALLET_JACK = "pallet_jack"
    CONVEYOR_SYSTEM = "conveyor_system"
    SORTING_MACHINE = "sorting_machine"
    LOADING_DOCK = "loading_dock"
    WAREHOUSE_SCANNER = "warehouse_scanner"
    GPS_TRACKER = "gps_tracker"
    REFRIGERATION_UNIT = "refrigeration_unit"
    CRANE_SYSTEM = "crane_system"
    AUTOMATED_STORAGE = "automated_storage"


class DeliveryStatus(Enum):
    """Delivery status types"""

    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    FAILED = "failed"
    RETURNED = "returned"


@dataclass
class LogisticsRoute:
    """Logistics route configuration"""

    route_id: str
    origin: str
    destination: str
    vehicle_id: str
    estimated_duration: timedelta
    cargo_capacity: float
    current_load: float = 0.0
    status: str = "planned"


@dataclass
class DeliveryIncident:
    """Delivery incident tracking"""

    incident_id: str
    route_id: str
    vehicle_id: str
    incident_type: str
    severity: str  # critical, high, medium, low
    description: str
    customer_impact: str
    estimated_delay: timedelta
    timestamp: datetime = None


class LogisticsAssistant(FixItFredCore):
    """
    Logistics-specific AI assistant
    Extends FixItFred with transportation and logistics expertise
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)

        # Logistics-specific data
        self.logistics_routes: Dict[str, LogisticsRoute] = {}
        self.delivery_incidents: Dict[str, DeliveryIncident] = {}
        self.fleet_performance: Dict[str, Dict] = {}

        logger.info("🚛 Logistics Assistant initialized")

    async def diagnose_fleet_vehicle(
        self,
        vehicle_id: str,
        symptoms: List[str],
        current_route: Optional[str] = None,
        cargo_status: str = "loaded",
    ) -> Dict[str, Any]:
        """
        Diagnose fleet vehicle with delivery impact assessment
        """
        vehicle = self.assets.get(vehicle_id)
        if not vehicle:
            return {"error": "Fleet vehicle not found"}

        route = self.logistics_routes.get(current_route) if current_route else None
        route_context = (
            f"Route: {route.origin} → {route.destination}"
            if route
            else "Route: Not assigned"
        )

        prompt = f"""FLEET VEHICLE DIAGNOSIS:

Vehicle: {vehicle.name} ({vehicle.make} {vehicle.model})
Type: {vehicle.asset_type}
{route_context}
Cargo Status: {cargo_status}
Symptoms: {', '.join(symptoms)}

As a fleet management specialist, provide:

1. DELIVERY IMPACT ASSESSMENT
   - Immediate delivery disruption
   - Customer notification requirements
   - Alternative vehicle deployment
   - Route rescheduling options
   - Cargo protection measures

2. VEHICLE DIAGNOSIS
   - Engine and drivetrain analysis
   - Brake and suspension systems
   - Electrical system problems
   - Hydraulic system issues
   - Refrigeration unit status (if applicable)

3. OPERATIONAL RESPONSE
   - Roadside repair feasibility
   - Towing and recovery options
   - Cargo transfer procedures
   - Emergency service protocols
   - Driver safety considerations

4. SERVICE STRATEGY
   - Mobile repair unit deployment
   - Authorized service center options
   - Parts availability assessment
   - Repair time estimation
   - Cost analysis

5. FLEET OPTIMIZATION
   - Route redistribution
   - Backup vehicle activation
   - Load balancing adjustments
   - Service window planning
   - Performance monitoring

6. PREVENTIVE MEASURES
   - Predictive maintenance updates
   - Driver training enhancements
   - Vehicle inspection protocols
   - Fleet replacement planning
   - Technology upgrades

Prioritize delivery commitments and customer satisfaction."""

        try:
            if self.ai_team:
                responses = await self.ai_team.diagnose_with_ai_team(
                    prompt,
                    {"vehicle_type": vehicle.asset_type, "route_info": route_context},
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Assess delivery impact
                if route and cargo_status == "loaded":
                    estimated_delay = timedelta(hours=2)  # Default estimate
                    incident = DeliveryIncident(
                        incident_id=f"delivery_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        route_id=current_route,
                        vehicle_id=vehicle_id,
                        incident_type="vehicle_breakdown",
                        severity="high"
                        if "engine" in " ".join(symptoms).lower()
                        else "medium",
                        description=f"Vehicle breakdown: {', '.join(symptoms)}",
                        customer_impact="Delivery delay expected",
                        estimated_delay=estimated_delay,
                        timestamp=datetime.now(),
                    )
                    self.delivery_incidents[incident.incident_id] = incident

                return {
                    "vehicle_id": vehicle_id,
                    "current_route": current_route,
                    "diagnosis": best_response.content,
                    "confidence": best_response.confidence,
                    "ai_provider": best_response.provider.value,
                    "repair_instructions": best_response.fix_instructions,
                    "delivery_impact": {
                        "route_affected": bool(route),
                        "cargo_at_risk": cargo_status == "loaded",
                        "estimated_delay": "2-4 hours" if route else "N/A",
                    },
                    "operational_response": best_response.suggestions,
                    "delivery_incident_created": bool(
                        route and cargo_status == "loaded"
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                diagnosis = await self.think(prompt, task_type="fleet_diagnosis")
                return {
                    "vehicle_id": vehicle_id,
                    "current_route": current_route,
                    "diagnosis": diagnosis,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Fleet vehicle diagnosis error: {e}")
            return {"error": str(e)}

    async def optimize_delivery_routes(
        self,
        route_ids: List[str],
        traffic_data: Optional[Dict] = None,
        weather_conditions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        AI-powered delivery route optimization
        """
        routes = [
            self.logistics_routes.get(rid)
            for rid in route_ids
            if self.logistics_routes.get(rid)
        ]

        if not routes:
            return {"error": "No valid routes found"}

        prompt = f"""DELIVERY ROUTE OPTIMIZATION:

Routes Count: {len(routes)}
Routes: {[f"{r.origin} → {r.destination}" for r in routes]}
Traffic Data: {traffic_data if traffic_data else 'Not available'}
Weather Conditions: {weather_conditions if weather_conditions else 'Normal'}

LOGISTICS OPTIMIZATION ANALYSIS:

1. ROUTE EFFICIENCY
   - Distance optimization
   - Traffic pattern analysis
   - Fuel consumption minimization
   - Delivery time windows
   - Vehicle capacity utilization

2. REAL-TIME ADJUSTMENTS
   - Traffic congestion avoidance
   - Weather impact mitigation
   - Road closure rerouting
   - Construction zone navigation
   - Emergency response coordination

3. CUSTOMER SERVICE OPTIMIZATION
   - Delivery window accuracy
   - Customer notification timing
   - Preferred delivery times
   - Special handling requirements
   - Delivery attempt optimization

4. FLEET UTILIZATION
   - Vehicle assignment optimization
   - Load balancing strategies
   - Multi-stop route planning
   - Return trip optimization
   - Idle time minimization

5. COST OPTIMIZATION
   - Fuel efficiency improvements
   - Driver overtime reduction
   - Vehicle wear minimization
   - Toll route optimization
   - Maintenance impact consideration

6. PERFORMANCE METRICS
   - On-time delivery improvement
   - Customer satisfaction enhancement
   - Operational cost reduction
   - Environmental impact reduction
   - Driver efficiency gains

Provide actionable route optimization recommendations."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="logistics_optimization"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                return {
                    "route_optimization": best_response.content,
                    "confidence": best_response.confidence,
                    "routes_analyzed": len(routes),
                    "traffic_conditions": traffic_data,
                    "weather_factor": weather_conditions,
                    "recommended_changes": best_response.suggestions,
                    "implementation_steps": best_response.fix_instructions,
                    "expected_benefits": {
                        "delivery_time_improvement": "15-25%",
                        "fuel_savings": "10-20%",
                        "customer_satisfaction": "Improved on-time delivery",
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                optimization = await self.think(
                    prompt, task_type="logistics_optimization"
                )
                return {
                    "route_optimization": optimization,
                    "routes_analyzed": len(routes),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            return {"error": str(e)}

    async def create_fleet_maintenance_schedule(
        self, vehicle_ids: List[str], operational_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create logistics-optimized fleet maintenance schedule
        """
        vehicles = [self.assets.get(vid) for vid in vehicle_ids if self.assets.get(vid)]

        if not vehicles:
            return {"error": "No valid vehicles found"}

        prompt = f"""FLEET MAINTENANCE SCHEDULE OPTIMIZATION:

Fleet Size: {len(vehicles)}
Vehicle Types: {list(set([v.asset_type for v in vehicles]))}
Operational Requirements: {operational_requirements}

CREATE DELIVERY-OPTIMIZED MAINTENANCE SCHEDULE:

1. OPERATIONAL CONTINUITY
   - Peak delivery period avoidance
   - Route coverage maintenance
   - Customer commitment protection
   - Emergency backup planning
   - Service level maintenance

2. VEHICLE PRIORITIZATION
   - High-mileage vehicle focus
   - Critical route vehicle priority
   - Refrigerated unit maintenance
   - Safety system prioritization
   - Fuel efficiency optimization

3. PREDICTIVE MAINTENANCE
   - Mileage-based scheduling
   - Usage pattern analysis
   - Wear prediction modeling
   - Breakdown prevention strategies
   - Performance monitoring integration

4. COST EFFICIENCY
   - Bulk maintenance scheduling
   - Vendor consolidation
   - Warranty optimization
   - Downtime cost minimization
   - Fuel efficiency improvements

5. COMPLIANCE MANAGEMENT
   - DOT inspection requirements
   - Safety regulation compliance
   - Environmental standards
   - Insurance requirements
   - Fleet certification maintenance

6. PERFORMANCE OPTIMIZATION
   - Vehicle availability maximization
   - Route efficiency maintenance
   - Driver satisfaction considerations
   - Customer service continuity
   - Technology system updates

Schedule maintenance to maximize fleet availability and delivery reliability."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="fleet_maintenance"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create maintenance tasks for each vehicle
                tasks = []
                for vehicle in vehicles:
                    task = await self.create_task(
                        user_id="logistics_system",
                        asset_id=vehicle.asset_id,
                        title=f"Fleet maintenance - {vehicle.name}",
                        description="Delivery-optimized fleet maintenance",
                        priority=TaskPriority.MEDIUM,
                    )
                    tasks.append(task)

                return {
                    "maintenance_schedule": best_response.content,
                    "confidence": best_response.confidence,
                    "fleet_size": len(vehicles),
                    "created_tasks": len(tasks),
                    "operational_requirements": operational_requirements,
                    "optimization_focus": "Delivery reliability and fleet availability",
                    "recommendations": best_response.suggestions,
                    "implementation_plan": best_response.fix_instructions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                schedule = await self.think(prompt, task_type="fleet_maintenance")
                return {
                    "maintenance_schedule": schedule,
                    "fleet_size": len(vehicles),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Fleet maintenance schedule error: {e}")
            return {"error": str(e)}

    def register_logistics_route(
        self,
        route_id: str,
        origin: str,
        destination: str,
        vehicle_id: str,
        estimated_duration: timedelta,
        cargo_capacity: float,
    ) -> LogisticsRoute:
        """Register a new logistics route"""
        route = LogisticsRoute(
            route_id=route_id,
            origin=origin,
            destination=destination,
            vehicle_id=vehicle_id,
            estimated_duration=estimated_duration,
            cargo_capacity=cargo_capacity,
        )
        self.logistics_routes[route_id] = route
        logger.info(f"🚛 Registered logistics route: {origin} → {destination}")
        return route

    def register_fleet_vehicle(
        self,
        vehicle_id: str,
        name: str,
        vehicle_type: LogisticsEquipmentType,
        make: str,
        model: str,
        year: Optional[int] = None,
        capacity: Optional[float] = None,
    ) -> Asset:
        """Register fleet vehicle"""
        asset = Asset(
            asset_id=vehicle_id,
            name=name,
            asset_type=vehicle_type.value,
            make=make,
            model=model,
            year=year,
        )
        self.assets[vehicle_id] = asset
        logger.info(f"🚛 Registered fleet vehicle: {name} (Capacity: {capacity})")
        return asset

    async def get_logistics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive logistics dashboard data"""
        try:
            # Get delivery performance metrics
            critical_incidents = len(
                [
                    i
                    for i in self.delivery_incidents.values()
                    if i.severity == "critical"
                ]
            )
            total_delay_hours = sum(
                [
                    i.estimated_delay.total_seconds() / 3600
                    for i in self.delivery_incidents.values()
                ]
            )

            # Get fleet status
            active_routes = len(
                [r for r in self.logistics_routes.values() if r.status == "in_transit"]
            )
            total_fleet_capacity = sum(
                [r.cargo_capacity for r in self.logistics_routes.values()]
            )

            # Get maintenance status
            total_vehicles = len(self.assets)
            active_tasks = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
            )

            # Get AI team status if available
            ai_status = {}
            if self.ai_team:
                ai_status = self.ai_team.get_ai_team_status()

            return {
                "delivery_performance": {
                    "critical_incidents": critical_incidents,
                    "total_delay_hours": total_delay_hours,
                    "active_routes": active_routes,
                    "incident_count": len(self.delivery_incidents),
                },
                "fleet_status": {
                    "total_vehicles": total_vehicles,
                    "total_capacity": total_fleet_capacity,
                    "active_maintenance": active_tasks,
                    "vehicle_types": list(
                        set([a.asset_type for a in self.assets.values()])
                    ),
                },
                "operations": {
                    "total_routes": len(self.logistics_routes),
                    "route_statuses": {
                        status: len(
                            [
                                r
                                for r in self.logistics_routes.values()
                                if r.status == status
                            ]
                        )
                        for status in ["planned", "in_transit", "completed"]
                    },
                },
                "ai_team_status": ai_status,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Logistics dashboard error: {e}")
            return {"error": str(e)}


# Global logistics assistant instance
logistics_assistant = LogisticsAssistant()

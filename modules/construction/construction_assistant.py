#!/usr/bin/env python3
"""
FixItFred Construction Assistant Module
AI-powered construction equipment and project management
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


class ConstructionEquipmentType(Enum):
    """Construction equipment types"""

    EXCAVATOR = "excavator"
    BULLDOZER = "bulldozer"
    CRANE = "crane"
    LOADER = "loader"
    DUMP_TRUCK = "dump_truck"
    CONCRETE_MIXER = "concrete_mixer"
    GENERATOR = "generator"
    COMPRESSOR = "air_compressor"
    POWER_TOOLS = "power_tools"
    SCAFFOLDING = "scaffolding"
    FORKLIFT = "forklift"
    WELDING_EQUIPMENT = "welding_equipment"


class SafetyCategory(Enum):
    """Construction safety categories"""

    FALL_PROTECTION = "fall_protection"
    ELECTRICAL_SAFETY = "electrical_safety"
    HEAVY_MACHINERY = "heavy_machinery"
    STRUCTURAL_INTEGRITY = "structural_integrity"
    HAZMAT = "hazardous_materials"
    PERSONAL_PROTECTIVE = "personal_protective_equipment"


@dataclass
class ConstructionProject:
    """Construction project configuration"""

    project_id: str
    name: str
    location: str
    equipment_ids: List[str]
    start_date: datetime
    estimated_completion: datetime
    project_type: str = "commercial"
    safety_requirements: List[str] = None


@dataclass
class SafetyIncident:
    """Safety incident tracking"""

    incident_id: str
    project_id: str
    equipment_id: Optional[str]
    incident_type: str
    severity: str  # critical, high, medium, low
    description: str
    immediate_actions: List[str]
    investigation_required: bool
    timestamp: datetime = None


class ConstructionAssistant(FixItFredCore):
    """
    Construction-specific AI assistant
    Extends FixItFred with construction industry expertise
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)

        # Construction-specific data
        self.construction_projects: Dict[str, ConstructionProject] = {}
        self.safety_incidents: Dict[str, SafetyIncident] = {}
        self.weather_considerations: Dict[str, Dict] = {}

        logger.info("🏗️ Construction Assistant initialized")

    async def diagnose_construction_equipment(
        self,
        equipment_id: str,
        symptoms: List[str],
        project_id: str,
        safety_concerns: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Diagnose construction equipment with safety-first approach
        """
        equipment = self.assets.get(equipment_id)
        if not equipment:
            return {"error": "Construction equipment not found"}

        project = self.construction_projects.get(project_id)
        project_context = f"Project: {project.name}" if project else "Project: Unknown"

        prompt = f"""CONSTRUCTION EQUIPMENT DIAGNOSIS:

Equipment: {equipment.name} ({equipment.make} {equipment.model})
Type: {equipment.asset_type}
{project_context}
Symptoms: {', '.join(symptoms)}
Safety Concerns: {', '.join(safety_concerns) if safety_concerns else 'None reported'}

As a construction equipment specialist, provide:

1. SAFETY ASSESSMENT (PRIORITY #1)
   - Immediate safety hazards
   - Equipment shutdown requirements
   - Site evacuation protocols
   - Worker protection measures
   - Structural integrity risks

2. EQUIPMENT DIAGNOSIS
   - Hydraulic system analysis
   - Engine and powertrain issues
   - Electrical system problems
   - Structural component failures
   - Wear pattern assessment

3. PROJECT IMPACT ANALYSIS
   - Critical path disruption
   - Alternative equipment options
   - Schedule adjustment requirements
   - Cost implications
   - Resource reallocation needs

4. REPAIR STRATEGY
   - Field repair vs shop repair
   - Parts availability assessment
   - Certified technician requirements
   - Temporary solutions
   - Equipment rental considerations

5. PREVENTION MEASURES
   - Operator training improvements
   - Preventive maintenance updates
   - Environmental protection
   - Usage monitoring systems
   - Regular inspection protocols

6. REGULATORY COMPLIANCE
   - OSHA requirements
   - Equipment certification needs
   - Inspection documentation
   - Safety reporting obligations
   - Insurance considerations

SAFETY IS THE TOP PRIORITY - equipment must be secured before any repair work."""

        try:
            if self.ai_team:
                responses = await self.ai_team.diagnose_with_ai_team(
                    prompt,
                    {
                        "equipment_type": equipment.asset_type,
                        "safety_concerns": safety_concerns,
                    },
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create safety incident if safety concerns exist
                if safety_concerns:
                    incident = SafetyIncident(
                        incident_id=f"safety_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        project_id=project_id,
                        equipment_id=equipment_id,
                        incident_type="equipment_failure",
                        severity="high"
                        if any(
                            "critical" in concern.lower() for concern in safety_concerns
                        )
                        else "medium",
                        description=f"Equipment failure with safety implications: {', '.join(symptoms)}",
                        immediate_actions=[
                            "Equipment isolated",
                            "Site secured",
                            "Investigation initiated",
                        ],
                        investigation_required=True,
                        timestamp=datetime.now(),
                    )
                    self.safety_incidents[incident.incident_id] = incident

                return {
                    "equipment_id": equipment_id,
                    "project_id": project_id,
                    "diagnosis": best_response.content,
                    "confidence": best_response.confidence,
                    "ai_provider": best_response.provider.value,
                    "safety_actions": best_response.fix_instructions,
                    "safety_incident_created": bool(safety_concerns),
                    "project_impact": "Under assessment",
                    "immediate_shutdown_required": bool(safety_concerns),
                    "recommendations": best_response.suggestions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                diagnosis = await self.think(prompt, task_type="construction_diagnosis")
                return {
                    "equipment_id": equipment_id,
                    "project_id": project_id,
                    "diagnosis": diagnosis,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Construction equipment diagnosis error: {e}")
            return {"error": str(e)}

    async def optimize_project_timeline(
        self,
        project_id: str,
        current_status: Dict[str, Any],
        weather_forecast: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        AI-powered construction project timeline optimization
        """
        project = self.construction_projects.get(project_id)
        if not project:
            return {"error": "Construction project not found"}

        prompt = f"""CONSTRUCTION PROJECT OPTIMIZATION:

Project: {project.name}
Location: {project.location}
Start Date: {project.start_date.strftime('%Y-%m-%d')}
Estimated Completion: {project.estimated_completion.strftime('%Y-%m-%d')}
Current Status: {current_status.get('completion_percentage', 0):.1%} complete

Equipment Available: {len(project.equipment_ids)} units
Weather Forecast: {weather_forecast if weather_forecast else 'Not available'}

PROJECT OPTIMIZATION ANALYSIS:

1. CRITICAL PATH ANALYSIS
   - Task dependency mapping
   - Resource bottleneck identification
   - Equipment utilization optimization
   - Labor allocation efficiency

2. WEATHER IMPACT MITIGATION
   - Weather-sensitive activities
   - Indoor vs outdoor work scheduling
   - Equipment protection strategies
   - Alternative task sequencing

3. EQUIPMENT OPTIMIZATION
   - Multi-tasking opportunities
   - Equipment sharing strategies
   - Maintenance window planning
   - Replacement equipment needs

4. SAFETY INTEGRATION
   - Safety milestone planning
   - Risk assessment scheduling
   - Training integration
   - Inspection coordination

5. COST OPTIMIZATION
   - Resource efficiency improvements
   - Overtime minimization
   - Equipment rental optimization
   - Material delivery coordination

6. SCHEDULE RECOVERY
   - Fast-tracking opportunities
   - Parallel task execution
   - Resource augmentation
   - Scope optimization

Provide actionable timeline improvements with safety priorities."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="construction_optimization"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Store weather considerations
                if weather_forecast:
                    self.weather_considerations[project_id] = weather_forecast

                return {
                    "project_id": project_id,
                    "optimization_plan": best_response.content,
                    "confidence": best_response.confidence,
                    "current_status": current_status,
                    "weather_considerations": weather_forecast,
                    "recommended_actions": best_response.suggestions,
                    "implementation_steps": best_response.fix_instructions,
                    "expected_benefits": {
                        "schedule_improvement": "10-20% faster completion",
                        "cost_savings": "5-15% cost reduction",
                        "safety_enhancement": "Improved safety compliance",
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                optimization = await self.think(
                    prompt, task_type="construction_optimization"
                )
                return {
                    "project_id": project_id,
                    "optimization_plan": optimization,
                    "current_status": current_status,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Project optimization error: {e}")
            return {"error": str(e)}

    async def create_safety_maintenance_schedule(
        self, project_id: str, equipment_ids: List[str], safety_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Create safety-focused maintenance schedule
        """
        project = self.construction_projects.get(project_id)
        equipment_list = [
            self.assets.get(eid) for eid in equipment_ids if self.assets.get(eid)
        ]

        if not equipment_list:
            return {"error": "No valid equipment found"}

        prompt = f"""CONSTRUCTION SAFETY MAINTENANCE SCHEDULE:

Project: {project.name if project else 'Unknown'}
Equipment Count: {len(equipment_list)}
Equipment Types: {list(set([e.asset_type for e in equipment_list]))}
Safety Requirements: {', '.join(safety_requirements)}

CREATE SAFETY-FIRST MAINTENANCE SCHEDULE:

1. SAFETY PRIORITIZATION
   - Critical safety equipment first
   - High-risk operation preparation
   - Regulatory compliance timing
   - Emergency system readiness

2. OPERATIONAL COORDINATION
   - Project timeline integration
   - Minimal disruption scheduling
   - Weather window optimization
   - Resource availability alignment

3. PREVENTIVE MAINTENANCE
   - Manufacturer specifications
   - Heavy-duty usage adjustments
   - Environmental factor considerations
   - Operator feedback integration

4. INSPECTION PROTOCOLS
   - Daily safety checks
   - Weekly system inspections
   - Monthly comprehensive reviews
   - Annual certifications

5. EMERGENCY PREPAREDNESS
   - Backup equipment strategy
   - Rapid repair protocols
   - Emergency contact procedures
   - Site safety coordination

6. COMPLIANCE MANAGEMENT
   - OSHA requirement tracking
   - Equipment certification maintenance
   - Documentation standards
   - Training coordination

Safety and project continuity are equally important priorities."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="construction_maintenance"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create maintenance tasks for each equipment
                tasks = []
                for equipment in equipment_list:
                    task = await self.create_task(
                        user_id="construction_system",
                        asset_id=equipment.asset_id,
                        title=f"Construction safety maintenance - {equipment.name}",
                        description=f"Safety-focused maintenance for {project.name if project else 'project'}",
                        priority=TaskPriority.HIGH,
                    )
                    tasks.append(task)

                return {
                    "project_id": project_id,
                    "maintenance_schedule": best_response.content,
                    "confidence": best_response.confidence,
                    "equipment_count": len(equipment_list),
                    "created_tasks": len(tasks),
                    "safety_requirements": safety_requirements,
                    "focus_areas": "Safety compliance and project continuity",
                    "recommendations": best_response.suggestions,
                    "implementation_plan": best_response.fix_instructions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                schedule = await self.think(
                    prompt, task_type="construction_maintenance"
                )
                return {
                    "project_id": project_id,
                    "maintenance_schedule": schedule,
                    "equipment_count": len(equipment_list),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Construction maintenance schedule error: {e}")
            return {"error": str(e)}

    def register_construction_project(
        self,
        project_id: str,
        name: str,
        location: str,
        equipment_ids: List[str],
        start_date: datetime,
        estimated_completion: datetime,
    ) -> ConstructionProject:
        """Register a new construction project"""
        project = ConstructionProject(
            project_id=project_id,
            name=name,
            location=location,
            equipment_ids=equipment_ids,
            start_date=start_date,
            estimated_completion=estimated_completion,
        )
        self.construction_projects[project_id] = project
        logger.info(f"🏗️ Registered construction project: {name}")
        return project

    def register_construction_equipment(
        self,
        equipment_id: str,
        name: str,
        equipment_type: ConstructionEquipmentType,
        make: str,
        model: str,
        project_id: str,
        year: Optional[int] = None,
    ) -> Asset:
        """Register construction equipment"""
        asset = Asset(
            asset_id=equipment_id,
            name=name,
            asset_type=equipment_type.value,
            make=make,
            model=model,
            year=year,
        )
        self.assets[equipment_id] = asset
        logger.info(
            f"🏗️ Registered construction equipment: {name} (Project: {project_id})"
        )
        return asset

    async def get_construction_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive construction dashboard data"""
        try:
            # Get safety metrics
            critical_incidents = len(
                [i for i in self.safety_incidents.values() if i.severity == "critical"]
            )
            open_investigations = len(
                [i for i in self.safety_incidents.values() if i.investigation_required]
            )

            # Get project status
            active_projects = len(
                [
                    p
                    for p in self.construction_projects.values()
                    if p.estimated_completion > datetime.now()
                ]
            )
            overdue_projects = len(
                [
                    p
                    for p in self.construction_projects.values()
                    if p.estimated_completion < datetime.now()
                ]
            )

            # Get equipment status
            total_equipment = len(self.assets)
            active_tasks = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
            )

            # Get AI team status if available
            ai_status = {}
            if self.ai_team:
                ai_status = self.ai_team.get_ai_team_status()

            return {
                "safety": {
                    "critical_incidents": critical_incidents,
                    "open_investigations": open_investigations,
                    "total_safety_incidents": len(self.safety_incidents),
                },
                "projects": {
                    "active_projects": active_projects,
                    "overdue_projects": overdue_projects,
                    "total_projects": len(self.construction_projects),
                },
                "equipment": {
                    "total_equipment": total_equipment,
                    "active_maintenance": active_tasks,
                    "equipment_types": list(
                        set([a.asset_type for a in self.assets.values()])
                    ),
                },
                "ai_team_status": ai_status,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Construction dashboard error: {e}")
            return {"error": str(e)}


# Global construction assistant instance
construction_assistant = ConstructionAssistant()

#!/usr/bin/env python3
"""
FixItFred Manufacturing Assistant Module
AI-powered manufacturing maintenance and optimization
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


class EquipmentType(Enum):
    """Manufacturing equipment types"""

    CNC_MACHINE = "cnc_machine"
    CONVEYOR = "conveyor"
    ROBOT = "robot"
    PRESS = "press"
    PUMP = "pump"
    MOTOR = "motor"
    HVAC = "hvac"
    COMPRESSOR = "compressor"


class MaintenanceType(Enum):
    """Manufacturing maintenance types"""

    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"


@dataclass
class ProductionLine:
    """Production line configuration"""

    line_id: str
    name: str
    equipment_ids: List[str]
    capacity_per_hour: int
    current_status: str = "running"
    efficiency_target: float = 0.85


@dataclass
class QualityCheck:
    """Quality control check"""

    check_id: str
    equipment_id: str
    parameter: str
    target_value: float
    tolerance: float
    last_reading: Optional[float] = None
    status: str = "pending"


class ManufacturingAssistant(FixItFredCore):
    """
    Manufacturing-specific AI assistant
    Extends FixItFred with manufacturing expertise
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)

        # Manufacturing-specific data
        self.production_lines: Dict[str, ProductionLine] = {}
        self.quality_checks: Dict[str, QualityCheck] = {}
        self.equipment_sensors: Dict[str, Dict] = {}

        logger.info("🏭 Manufacturing Assistant initialized")

    async def diagnose_equipment_failure(
        self, equipment_id: str, symptoms: List[str], sensor_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Diagnose equipment failure using manufacturing expertise
        """
        equipment = self.assets.get(equipment_id)
        if not equipment:
            return {"error": "Equipment not found"}

        # Build manufacturing-specific diagnostic prompt
        prompt = f"""MANUFACTURING EQUIPMENT DIAGNOSIS:

Equipment: {equipment.name} ({equipment.make} {equipment.model})
Type: {equipment.asset_type}
Symptoms: {', '.join(symptoms)}

Sensor Data: {sensor_data if sensor_data else 'Not available'}

As an expert in manufacturing maintenance, provide:

1. ROOT CAUSE ANALYSIS
   - Most likely failure modes (ranked by probability)
   - Component-specific diagnostics
   - Wear pattern analysis

2. IMPACT ASSESSMENT
   - Production downtime risk
   - Safety implications
   - Quality impact

3. REPAIR STRATEGY
   - Immediate actions (stop/continue production)
   - Temporary fixes vs permanent repair
   - Required expertise level
   - Parts and tools needed

4. PREVENTION
   - Predictive maintenance recommendations
   - Sensor monitoring setup
   - Maintenance schedule adjustments

5. COST ANALYSIS
   - Repair cost estimate
   - Downtime cost per hour
   - ROI of preventive measures

Format as detailed manufacturing report."""

        try:
            # Use AI team for advanced diagnosis
            if self.ai_team:
                responses = await self.ai_team.diagnose_with_ai_team(
                    prompt,
                    {
                        "equipment_type": equipment.asset_type,
                        "sensor_data": sensor_data,
                    },
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                return {
                    "equipment_id": equipment_id,
                    "diagnosis": best_response.content,
                    "confidence": best_response.confidence,
                    "ai_provider": best_response.provider.value,
                    "fix_instructions": best_response.fix_instructions,
                    "symptoms": symptoms,
                    "sensor_data": sensor_data,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Fallback diagnosis
                diagnosis = await self.think(prompt, task_type="diagnosis")
                return {
                    "equipment_id": equipment_id,
                    "diagnosis": diagnosis,
                    "symptoms": symptoms,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Equipment diagnosis error: {e}")
            return {"error": str(e)}

    async def optimize_production_line(
        self, line_id: str, current_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        AI-powered production line optimization
        """
        line = self.production_lines.get(line_id)
        if not line:
            return {"error": "Production line not found"}

        prompt = f"""PRODUCTION LINE OPTIMIZATION:

Line: {line.name}
Current Metrics:
- Efficiency: {current_metrics.get('efficiency', 0):.1%}
- Throughput: {current_metrics.get('throughput', 0)} units/hour
- Downtime: {current_metrics.get('downtime', 0)} hours/day
- Quality Rate: {current_metrics.get('quality_rate', 0):.1%}
- OEE: {current_metrics.get('oee', 0):.1%}

Target Efficiency: {line.efficiency_target:.1%}
Line Capacity: {line.capacity_per_hour} units/hour

OPTIMIZATION ANALYSIS:

1. BOTTLENECK IDENTIFICATION
   - Equipment constraints
   - Process limitations
   - Resource constraints

2. IMPROVEMENT OPPORTUNITIES
   - Setup time reduction
   - Cycle time optimization
   - Quality improvements
   - Maintenance optimization

3. RECOMMENDED ACTIONS
   - Immediate improvements (0-30 days)
   - Short-term projects (1-3 months)
   - Long-term investments (3-12 months)

4. EXPECTED RESULTS
   - Efficiency gains
   - Cost savings
   - ROI calculations
   - Implementation timeline

Provide specific, actionable recommendations."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="optimization"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                return {
                    "line_id": line_id,
                    "optimization_plan": best_response.content,
                    "confidence": best_response.confidence,
                    "recommendations": best_response.suggestions,
                    "current_metrics": current_metrics,
                    "target_efficiency": line.efficiency_target,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                optimization = await self.think(prompt, task_type="optimization")
                return {
                    "line_id": line_id,
                    "optimization_plan": optimization,
                    "current_metrics": current_metrics,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Production optimization error: {e}")
            return {"error": str(e)}

    async def create_predictive_maintenance_schedule(
        self, equipment_ids: List[str], historical_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create AI-optimized predictive maintenance schedule
        """
        equipment_list = [
            self.assets.get(eid) for eid in equipment_ids if self.assets.get(eid)
        ]

        if not equipment_list:
            return {"error": "No valid equipment found"}

        prompt = f"""PREDICTIVE MAINTENANCE SCHEDULE CREATION:

Equipment Count: {len(equipment_list)}
Equipment Types: {list(set([e.asset_type for e in equipment_list]))}

Historical Data Available: {bool(historical_data)}

CREATE OPTIMIZED MAINTENANCE SCHEDULE:

1. EQUIPMENT ANALYSIS
   - Criticality assessment
   - Failure mode analysis
   - Maintenance history review

2. SCHEDULE OPTIMIZATION
   - Condition-based intervals
   - Production impact minimization
   - Resource optimization
   - Cost-benefit analysis

3. MONITORING STRATEGY
   - Key performance indicators
   - Sensor requirements
   - Inspection points
   - Data collection methods

4. IMPLEMENTATION PLAN
   - Phased rollout
   - Training requirements
   - Tool and parts inventory
   - Budget requirements

5. SUCCESS METRICS
   - Downtime reduction targets
   - Cost savings projections
   - Reliability improvements
   - ROI expectations

Provide detailed schedule with specific timelines."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="optimization"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create maintenance tasks for each equipment
                tasks = []
                for equipment in equipment_list:
                    task = await self.create_task(
                        user_id="manufacturing_system",
                        asset_id=equipment.asset_id,
                        title=f"Predictive maintenance - {equipment.name}",
                        description="AI-optimized predictive maintenance",
                        priority=TaskPriority.MEDIUM,
                    )
                    tasks.append(task)

                return {
                    "schedule": best_response.content,
                    "confidence": best_response.confidence,
                    "equipment_count": len(equipment_list),
                    "created_tasks": len(tasks),
                    "recommendations": best_response.suggestions,
                    "implementation_steps": best_response.fix_instructions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                schedule = await self.think(prompt, task_type="optimization")
                return {
                    "schedule": schedule,
                    "equipment_count": len(equipment_list),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Predictive maintenance error: {e}")
            return {"error": str(e)}

    async def quality_control_analysis(
        self,
        product_batch: str,
        quality_metrics: Dict[str, float],
        specification_limits: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """
        AI-powered quality control analysis
        """
        prompt = f"""QUALITY CONTROL ANALYSIS:

Product Batch: {product_batch}

Quality Metrics:
{chr(10).join([f"- {k}: {v}" for k, v in quality_metrics.items()])}

Specification Limits:
{chr(10).join([f"- {k}: {v}" for k, v in specification_limits.items()])}

QUALITY ANALYSIS:

1. CONFORMANCE ASSESSMENT
   - Specification compliance
   - Statistical analysis
   - Trend identification
   - Capability analysis

2. NON-CONFORMANCE INVESTIGATION
   - Root cause analysis
   - Process variation sources
   - Equipment contribution
   - Material factors

3. CORRECTIVE ACTIONS
   - Immediate containment
   - Process adjustments
   - Equipment calibration
   - Training needs

4. PREVENTIVE MEASURES
   - Control plan updates
   - Monitoring enhancements
   - Process improvements
   - Supplier actions

5. IMPACT ASSESSMENT
   - Customer risk
   - Cost implications
   - Production impact
   - Regulatory compliance

Provide detailed quality assessment with recommendations."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="analysis"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Determine if batch passes quality standards
                out_of_spec = []
                for metric, value in quality_metrics.items():
                    limits = specification_limits.get(metric, {})
                    if limits:
                        if value < limits.get(
                            "min", float("-inf")
                        ) or value > limits.get("max", float("inf")):
                            out_of_spec.append(metric)

                return {
                    "batch": product_batch,
                    "quality_analysis": best_response.content,
                    "confidence": best_response.confidence,
                    "pass_fail": "FAIL" if out_of_spec else "PASS",
                    "out_of_spec_metrics": out_of_spec,
                    "corrective_actions": best_response.fix_instructions,
                    "recommendations": best_response.suggestions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                analysis = await self.think(prompt, task_type="analysis")
                return {
                    "batch": product_batch,
                    "quality_analysis": analysis,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Quality control error: {e}")
            return {"error": str(e)}

    def register_production_line(
        self, line_id: str, name: str, equipment_ids: List[str], capacity_per_hour: int
    ) -> ProductionLine:
        """Register a new production line"""
        line = ProductionLine(
            line_id=line_id,
            name=name,
            equipment_ids=equipment_ids,
            capacity_per_hour=capacity_per_hour,
        )
        self.production_lines[line_id] = line
        logger.info(f"🏭 Registered production line: {name}")
        return line

    def register_manufacturing_equipment(
        self,
        equipment_id: str,
        name: str,
        equipment_type: EquipmentType,
        make: str,
        model: str,
        year: Optional[int] = None,
    ) -> Asset:
        """Register manufacturing equipment"""
        asset = Asset(
            asset_id=equipment_id,
            name=name,
            asset_type=equipment_type.value,
            make=make,
            model=model,
            year=year,
        )
        self.assets[equipment_id] = asset
        logger.info(f"🔧 Registered equipment: {name}")
        return asset

    async def get_manufacturing_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive manufacturing dashboard data"""
        try:
            # Get overall equipment effectiveness
            total_equipment = len(self.assets)
            active_tasks = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
            )
            pending_tasks = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            )

            # Get AI team status if available
            ai_status = {}
            if self.ai_team:
                ai_status = self.ai_team.get_ai_team_status()

            return {
                "overview": {
                    "total_equipment": total_equipment,
                    "production_lines": len(self.production_lines),
                    "active_maintenance": active_tasks,
                    "pending_maintenance": pending_tasks,
                },
                "ai_team_status": ai_status,
                "production_lines": list(self.production_lines.keys()),
                "equipment_types": list(
                    set([a.asset_type for a in self.assets.values()])
                ),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return {"error": str(e)}


# Global manufacturing assistant instance
manufacturing_assistant = ManufacturingAssistant()

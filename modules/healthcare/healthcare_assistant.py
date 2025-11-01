#!/usr/bin/env python3
"""
FixItFred Healthcare Assistant Module
AI-powered medical equipment and facility maintenance
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


class MedicalEquipmentType(Enum):
    """Medical equipment types"""

    MRI = "mri_scanner"
    CT_SCANNER = "ct_scanner"
    XRAY = "xray_machine"
    ULTRASOUND = "ultrasound"
    VENTILATOR = "ventilator"
    PATIENT_MONITOR = "patient_monitor"
    DEFIBRILLATOR = "defibrillator"
    INFUSION_PUMP = "infusion_pump"
    HVAC_MEDICAL = "hvac_medical"
    STERILIZER = "sterilizer"


class ComplianceStandard(Enum):
    """Healthcare compliance standards"""

    FDA = "fda"
    HIPAA = "hipaa"
    JOINT_COMMISSION = "joint_commission"
    ISO_13485 = "iso_13485"
    IEC_60601 = "iec_60601"


@dataclass
class PatientSafetyAlert:
    """Patient safety alert"""

    alert_id: str
    equipment_id: str
    severity: str  # critical, high, medium, low
    description: str
    impact_assessment: str
    immediate_action: str
    timestamp: datetime = None


@dataclass
class ComplianceCheck:
    """Compliance verification check"""

    check_id: str
    equipment_id: str
    standard: ComplianceStandard
    requirement: str
    status: str = "pending"
    last_verified: Optional[datetime] = None
    next_due: Optional[datetime] = None


class HealthcareAssistant(FixItFredCore):
    """
    Healthcare-specific AI assistant
    Extends FixItFred with medical equipment expertise
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)

        # Healthcare-specific data
        self.safety_alerts: Dict[str, PatientSafetyAlert] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.medical_protocols: Dict[str, Dict] = {}

        logger.info("🏥 Healthcare Assistant initialized")

    async def diagnose_medical_equipment(
        self, equipment_id: str, symptoms: List[str], patient_impact: str = "none"
    ) -> Dict[str, Any]:
        """
        Diagnose medical equipment with patient safety focus
        """
        equipment = self.assets.get(equipment_id)
        if not equipment:
            return {"error": "Medical equipment not found"}

        prompt = f"""MEDICAL EQUIPMENT DIAGNOSIS:

Equipment: {equipment.name} ({equipment.make} {equipment.model})
Type: {equipment.asset_type}
Symptoms: {', '.join(symptoms)}
Patient Impact: {patient_impact}

As a medical equipment specialist, provide:

1. CRITICAL SAFETY ASSESSMENT
   - Immediate patient safety risks
   - Equipment shutdown recommendations
   - Emergency protocols to follow
   - Staff safety considerations

2. TECHNICAL DIAGNOSIS
   - Most likely failure modes
   - Component analysis (imaging, electrical, mechanical)
   - Calibration status assessment
   - Software/firmware issues

3. COMPLIANCE IMPLICATIONS
   - FDA reporting requirements
   - Joint Commission standards
   - Quality assurance protocols
   - Documentation requirements

4. REPAIR STRATEGY
   - Immediate containment actions
   - Authorized service provider requirements
   - OEM vs third-party repair options
   - Validation and testing protocols

5. PATIENT CARE CONTINUITY
   - Alternative equipment options
   - Case scheduling adjustments
   - Clinical workflow modifications
   - Communication protocols

6. REGULATORY COMPLIANCE
   - Incident reporting requirements
   - Documentation standards
   - Validation protocols
   - Risk management procedures

Prioritize patient safety above all other considerations."""

        try:
            if self.ai_team:
                responses = await self.ai_team.diagnose_with_ai_team(
                    prompt,
                    {
                        "equipment_type": equipment.asset_type,
                        "patient_impact": patient_impact,
                    },
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create safety alert if critical
                if patient_impact in ["critical", "high"]:
                    alert = PatientSafetyAlert(
                        alert_id=f"alert_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        equipment_id=equipment_id,
                        severity=patient_impact,
                        description=f"Equipment failure: {', '.join(symptoms)}",
                        impact_assessment=best_response.content[:200],
                        immediate_action="Equipment isolation pending assessment",
                        timestamp=datetime.now(),
                    )
                    self.safety_alerts[alert.alert_id] = alert

                return {
                    "equipment_id": equipment_id,
                    "diagnosis": best_response.content,
                    "confidence": best_response.confidence,
                    "ai_provider": best_response.provider.value,
                    "safety_actions": best_response.fix_instructions,
                    "patient_impact": patient_impact,
                    "safety_alert_created": patient_impact in ["critical", "high"],
                    "compliance_review_required": True,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                diagnosis = await self.think(prompt, task_type="medical_diagnosis")
                return {
                    "equipment_id": equipment_id,
                    "diagnosis": diagnosis,
                    "patient_impact": patient_impact,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Medical equipment diagnosis error: {e}")
            return {"error": str(e)}

    async def create_compliance_schedule(
        self, equipment_ids: List[str], standards: List[ComplianceStandard]
    ) -> Dict[str, Any]:
        """
        Create AI-optimized compliance and maintenance schedule
        """
        equipment_list = [
            self.assets.get(eid) for eid in equipment_ids if self.assets.get(eid)
        ]

        if not equipment_list:
            return {"error": "No valid medical equipment found"}

        prompt = f"""MEDICAL EQUIPMENT COMPLIANCE SCHEDULE:

Equipment Count: {len(equipment_list)}
Equipment Types: {list(set([e.asset_type for e in equipment_list]))}
Compliance Standards: {[s.value for s in standards]}

CREATE COMPREHENSIVE COMPLIANCE SCHEDULE:

1. REGULATORY REQUIREMENTS
   - FDA device regulations
   - Joint Commission standards
   - State health department requirements
   - Manufacturer specifications

2. PREVENTIVE MAINTENANCE
   - OEM recommended schedules
   - Performance verification protocols
   - Calibration requirements
   - Safety testing procedures

3. QUALITY ASSURANCE
   - Performance testing intervals
   - Accuracy verification
   - Image quality assessments
   - Electrical safety testing

4. DOCUMENTATION PROTOCOLS
   - Maintenance logs
   - Performance records
   - Incident reports
   - Compliance certificates

5. TRAINING REQUIREMENTS
   - Staff competency validation
   - Equipment operation training
   - Safety protocol updates
   - Emergency procedures

6. RISK MANAGEMENT
   - Equipment lifecycle planning
   - Obsolescence management
   - Vendor performance monitoring
   - Alternative equipment planning

Ensure all schedules meet patient safety and regulatory requirements."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="compliance_planning"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create compliance checks and maintenance tasks
                tasks = []
                compliance_checks = []

                for equipment in equipment_list:
                    # Create maintenance task
                    task = await self.create_task(
                        user_id="healthcare_system",
                        asset_id=equipment.asset_id,
                        title=f"Medical equipment compliance - {equipment.name}",
                        description="AI-optimized compliance and preventive maintenance",
                        priority=TaskPriority.HIGH,
                    )
                    tasks.append(task)

                    # Create compliance checks for each standard
                    for standard in standards:
                        check = ComplianceCheck(
                            check_id=f"check_{equipment.asset_id}_{standard.value}_{datetime.now().strftime('%Y%m%d')}",
                            equipment_id=equipment.asset_id,
                            standard=standard,
                            requirement=f"{standard.value} compliance verification",
                            next_due=datetime.now() + timedelta(days=30),
                        )
                        compliance_checks.append(check)
                        self.compliance_checks[check.check_id] = check

                return {
                    "compliance_schedule": best_response.content,
                    "confidence": best_response.confidence,
                    "equipment_count": len(equipment_list),
                    "created_tasks": len(tasks),
                    "compliance_checks": len(compliance_checks),
                    "standards_covered": [s.value for s in standards],
                    "recommendations": best_response.suggestions,
                    "implementation_plan": best_response.fix_instructions,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                schedule = await self.think(prompt, task_type="compliance_planning")
                return {
                    "compliance_schedule": schedule,
                    "equipment_count": len(equipment_list),
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Compliance schedule error: {e}")
            return {"error": str(e)}

    async def patient_safety_analysis(
        self,
        incident_description: str,
        equipment_involved: List[str],
        severity_level: str,
    ) -> Dict[str, Any]:
        """
        AI-powered patient safety incident analysis
        """
        prompt = f"""PATIENT SAFETY INCIDENT ANALYSIS:

Incident Description: {incident_description}
Equipment Involved: {', '.join(equipment_involved)}
Severity Level: {severity_level}

COMPREHENSIVE SAFETY ANALYSIS:

1. ROOT CAUSE INVESTIGATION
   - Equipment failure modes
   - Human factors analysis
   - Process breakdown points
   - Environmental factors

2. IMMEDIATE ACTIONS
   - Patient care priorities
   - Equipment isolation protocols
   - Staff notification procedures
   - Documentation requirements

3. RISK ASSESSMENT
   - Patient harm potential
   - Recurrence probability
   - Systemic vulnerabilities
   - Regulatory implications

4. CORRECTIVE MEASURES
   - Equipment modifications
   - Process improvements
   - Training enhancements
   - Policy updates

5. PREVENTIVE STRATEGIES
   - Proactive monitoring
   - Early warning systems
   - Staff education programs
   - Technology solutions

6. REGULATORY COMPLIANCE
   - Reporting obligations
   - Investigation protocols
   - Documentation standards
   - Follow-up requirements

Focus on patient safety and systematic prevention."""

        try:
            if self.ai_team:
                responses = await self.ai_team.collaborate_with_ai_team(
                    prompt, task_type="safety_analysis"
                )

                best_response = max(responses.values(), key=lambda x: x.confidence)

                # Create safety alert
                alert = PatientSafetyAlert(
                    alert_id=f"safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    equipment_id=equipment_involved[0]
                    if equipment_involved
                    else "multiple",
                    severity=severity_level,
                    description=incident_description,
                    impact_assessment=best_response.content[:300],
                    immediate_action="Under investigation - follow safety protocols",
                )
                self.safety_alerts[alert.alert_id] = alert

                return {
                    "incident_analysis": best_response.content,
                    "confidence": best_response.confidence,
                    "severity_level": severity_level,
                    "safety_alert_id": alert.alert_id,
                    "corrective_actions": best_response.fix_instructions,
                    "preventive_measures": best_response.suggestions,
                    "equipment_involved": equipment_involved,
                    "regulatory_reporting_required": severity_level
                    in ["critical", "high"],
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                analysis = await self.think(prompt, task_type="safety_analysis")
                return {
                    "incident_analysis": analysis,
                    "severity_level": severity_level,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Safety analysis error: {e}")
            return {"error": str(e)}

    def register_medical_equipment(
        self,
        equipment_id: str,
        name: str,
        equipment_type: MedicalEquipmentType,
        make: str,
        model: str,
        serial_number: str,
        year: Optional[int] = None,
    ) -> Asset:
        """Register medical equipment with enhanced tracking"""
        asset = Asset(
            asset_id=equipment_id,
            name=name,
            asset_type=equipment_type.value,
            make=make,
            model=model,
            year=year,
            serial_number=serial_number,
        )
        self.assets[equipment_id] = asset
        logger.info(f"🏥 Registered medical equipment: {name}")
        return asset

    async def get_healthcare_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive healthcare dashboard data"""
        try:
            # Get safety metrics
            critical_alerts = len(
                [a for a in self.safety_alerts.values() if a.severity == "critical"]
            )
            high_alerts = len(
                [a for a in self.safety_alerts.values() if a.severity == "high"]
            )

            # Get compliance status
            overdue_compliance = len(
                [
                    c
                    for c in self.compliance_checks.values()
                    if c.next_due and c.next_due < datetime.now()
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
                "patient_safety": {
                    "critical_alerts": critical_alerts,
                    "high_priority_alerts": high_alerts,
                    "total_safety_alerts": len(self.safety_alerts),
                },
                "compliance": {
                    "overdue_checks": overdue_compliance,
                    "total_compliance_items": len(self.compliance_checks),
                    "compliance_rate": max(
                        0,
                        1 - (overdue_compliance / max(1, len(self.compliance_checks))),
                    ),
                },
                "equipment": {
                    "total_medical_equipment": total_equipment,
                    "active_maintenance": active_tasks,
                    "equipment_types": list(
                        set([a.asset_type for a in self.assets.values()])
                    ),
                },
                "ai_team_status": ai_status,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Healthcare dashboard error: {e}")
            return {"error": str(e)}


# Global healthcare assistant instance
healthcare_assistant = HealthcareAssistant()

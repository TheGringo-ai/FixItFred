#!/usr/bin/env python3
"""
FixItFred AI Identity Core
Central identity and authorization system for all modules
"""

import asyncio
import json
import uuid
# JWT and cryptography are optional
try:
    import jwt
except ImportError:
    jwt = None

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import hmac

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:
    serialization = rsa = None

@dataclass
class UserClaims:
    """User identity and context claims"""
    user_id: str
    tenant: str
    name: str
    email: str
    roles: List[str]
    department: str
    site: Optional[str] = None
    shift: Optional[str] = None
    security_level: str = "standard"
    device_trust: str = "trusted"
    
@dataclass
class ModuleAccess:
    """Module-specific access permissions"""
    module: str
    roles: List[str]
    permissions: List[str]
    abac_context: Dict[str, Any]
    data_access_level: str = "full"  # full, restricted, read_only
    
@dataclass
class AIIdentityToken:
    """Short-lived token for module access"""
    sub: str  # user:tenant:user_id
    tenant: str
    module: str
    roles: List[str]
    permissions: List[str]
    abac: Dict[str, Any]
    exp: int
    iss: str = "https://id.fixitfred.ai/ai_identity_core"
    
class AIIdentityCore:
    """Central AI-driven identity and authorization system"""
    
    def __init__(self):
        self.issuer = "https://id.fixitfred.ai/ai_identity_core"
        self.token_lifetime = 900  # 15 minutes
        self.refresh_threshold = 300  # 5 minutes
        
        # Generate RSA key pair for JWT signing
        self.private_key, self.public_key = self._generate_key_pair()
        self.jwks = self._generate_jwks()
        
        # Module registry and policies
        self.module_registry: Dict[str, Dict[str, Any]] = {}
        self.tenant_policies: Dict[str, Dict[str, Any]] = {}
        self.user_contexts: Dict[str, UserClaims] = {}
        
    def _generate_key_pair(self):
        """Generate RSA key pair for JWT signing"""
        if rsa and serialization:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            return private_key, public_key
        else:
            # Fallback when cryptography is not available
            return None, None
    
    def _generate_jwks(self) -> Dict[str, Any]:
        """Generate JWKS for public key distribution"""
        if self.public_key and serialization:
            try:
                public_pem = self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                return {
                    "keys": [{
                        "kty": "RSA",
                        "use": "sig",
                        "alg": "RS256",
                        "kid": "fixitfred-ai-identity-1",
                        "n": "placeholder_modulus",  # Would extract from actual key
                        "e": "AQAB"
                    }]
                }
            except Exception:
                pass
        
        # Fallback JWKS
        return {
            "keys": [{
                "kty": "RSA",
                "use": "sig",
                "alg": "HS256",
                "kid": "fixitfred-fallback-1",
                "n": "fallback_key",
                "e": "AQAB"
            }]
        }
    
    async def register_module(self, module_name: str, module_config: Dict[str, Any]):
        """Register a module with its authentication requirements"""
        
        auth_config = {
            "module": module_name,
            "required_claims": module_config.get("required_claims", ["tenant", "module", "roles"]),
            "rbac": module_config.get("rbac", {}),
            "abac": module_config.get("abac", {}),
            "pii_fields": module_config.get("pii_fields", []),
            "data_classification": module_config.get("data_classification", "internal"),
            "encryption_required": module_config.get("encryption_required", True)
        }
        
        self.module_registry[module_name] = auth_config
        print(f"🔐 Registered module: {module_name}")
        
    async def authenticate_user(self, tenant: str, user_id: str, 
                              auth_context: Dict[str, Any]) -> UserClaims:
        """Authenticate user and gather identity context"""
        
        # In production, this would integrate with SSO provider
        user_claims = UserClaims(
            user_id=user_id,
            tenant=tenant,
            name=auth_context.get("name", user_id),
            email=auth_context.get("email", f"{user_id}@{tenant}.com"),
            roles=auth_context.get("roles", ["USER"]),
            department=auth_context.get("department", "general"),
            site=auth_context.get("site"),
            shift=auth_context.get("shift"),
            security_level=auth_context.get("security_level", "standard"),
            device_trust=auth_context.get("device_trust", "trusted")
        )
        
        # Cache user context
        cache_key = f"{tenant}:{user_id}"
        self.user_contexts[cache_key] = user_claims
        
        return user_claims
    
    async def authorize_module_access(self, user_claims: UserClaims, 
                                    module_name: str, 
                                    requested_permissions: List[str] = None) -> ModuleAccess:
        """AI-driven authorization for module access"""
        
        if module_name not in self.module_registry:
            raise ValueError(f"Module {module_name} not registered")
        
        module_config = self.module_registry[module_name]
        
        # AI analyzes user context and determines appropriate access
        ai_decision = await self._ai_authorize(user_claims, module_config, requested_permissions)
        
        # Build ABAC context
        abac_context = {
            "site": user_claims.site,
            "department": user_claims.department,
            "shift": user_claims.shift,
            "security_level": user_claims.security_level,
            "device_trust": user_claims.device_trust,
            "data_classification": module_config.get("data_classification", "internal")
        }
        
        module_access = ModuleAccess(
            module=module_name,
            roles=ai_decision["effective_roles"],
            permissions=ai_decision["granted_permissions"],
            abac_context=abac_context,
            data_access_level=ai_decision["data_access_level"]
        )
        
        return module_access
    
    async def _ai_authorize(self, user_claims: UserClaims, 
                          module_config: Dict[str, Any],
                          requested_permissions: List[str] = None) -> Dict[str, Any]:
        """AI-driven authorization decision"""
        
        # Simulate AI decision-making process
        # In production, this would use actual AI models
        
        base_roles = user_claims.roles
        effective_roles = base_roles.copy()
        
        # AI enhances roles based on context
        if user_claims.security_level == "high":
            if "ADMIN" not in effective_roles:
                effective_roles.append("ELEVATED")
        
        if user_claims.department == "quality" and "quality" in module_config["module"]:
            effective_roles.append("DOMAIN_EXPERT")
            
        # AI determines permissions
        module_rbac = module_config.get("rbac", {})
        all_permissions = []
        
        for role in effective_roles:
            role_permissions = module_rbac.get("permissions", {}).get(role, [])
            all_permissions.extend(role_permissions)
        
        # Remove duplicates
        granted_permissions = list(set(all_permissions))
        
        # AI determines data access level
        if "ADMIN" in effective_roles:
            data_access_level = "full"
        elif "MANAGER" in effective_roles:
            data_access_level = "department"
        else:
            data_access_level = "restricted"
        
        return {
            "effective_roles": effective_roles,
            "granted_permissions": granted_permissions,
            "data_access_level": data_access_level,
            "ai_reasoning": f"Enhanced roles based on {user_claims.security_level} security level and {user_claims.department} department context"
        }
    
    async def issue_module_token(self, user_claims: UserClaims, 
                               module_access: ModuleAccess) -> str:
        """Issue short-lived JWT token for module access"""
        
        now = int(time.time())
        exp = now + self.token_lifetime
        
        token_claims = {
            "sub": f"user:{user_claims.tenant}:{user_claims.user_id}",
            "tenant": user_claims.tenant,
            "module": module_access.module,
            "roles": module_access.roles,
            "permissions": module_access.permissions,
            "abac": module_access.abac_context,
            "data_access": module_access.data_access_level,
            "iat": now,
            "exp": exp,
            "iss": self.issuer,
            "jti": str(uuid.uuid4())
        }
        
        # Sign token with private key
        token = jwt.encode(
            token_claims,
            self.private_key,
            algorithm="RS256",
            headers={"kid": "fixitfred-ai-identity-1"}
        )
        
        # Log token issuance for audit
        await self._audit_log("token_issued", {
            "user": user_claims.user_id,
            "tenant": user_claims.tenant,
            "module": module_access.module,
            "roles": module_access.roles,
            "permissions": len(module_access.permissions),
            "expires": exp
        })
        
        return token
    
    async def verify_token(self, token: str, required_module: str = None) -> Dict[str, Any]:
        """Verify and decode module token"""
        
        try:
            # Decode and verify token
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.issuer
            )
            
            # Check module match if required
            if required_module and claims.get("module") != required_module:
                raise ValueError(f"Token not valid for module {required_module}")
            
            # Check expiration buffer for refresh
            exp = claims.get("exp", 0)
            now = int(time.time())
            
            if exp - now < self.refresh_threshold:
                claims["needs_refresh"] = True
            
            return claims
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    async def refresh_token(self, old_token: str) -> str:
        """Refresh an expiring token"""
        
        claims = await self.verify_token(old_token)
        
        # Get user context
        tenant = claims["tenant"]
        user_id = claims["sub"].split(":")[-1]
        cache_key = f"{tenant}:{user_id}"
        
        if cache_key not in self.user_contexts:
            raise ValueError("User context not found for refresh")
        
        user_claims = self.user_contexts[cache_key]
        
        # Re-authorize (AI may change permissions based on new context)
        module_access = await self.authorize_module_access(
            user_claims, 
            claims["module"]
        )
        
        # Issue new token
        return await self.issue_module_token(user_claims, module_access)
    
    async def revoke_token(self, token: str, reason: str = "manual_revocation"):
        """Revoke a token (add to blacklist)"""
        
        claims = await self.verify_token(token)
        jti = claims.get("jti")
        
        # In production, this would add to Redis blacklist
        await self._audit_log("token_revoked", {
            "jti": jti,
            "user": claims.get("sub"),
            "tenant": claims.get("tenant"),
            "reason": reason
        })
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JWKS for public key verification"""
        return self.jwks
    
    async def _audit_log(self, event: str, data: Dict[str, Any]):
        """Log security events for audit trail"""
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data,
            "source": "ai_identity_core"
        }
        
        # In production, this would go to secure audit log
        print(f"🔍 AUDIT: {event} - {json.dumps(data)}")

# Global AI Identity Core instance
ai_identity_core = AIIdentityCore()

# Module registration helper
async def register_fixitfred_modules():
    """Register all FixItFred modules with identity core"""
    
    modules = {
        "quality": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "INSPECTOR", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["quality.view", "reports.view"],
                    "INSPECTOR": ["quality.view", "quality.inspect", "defects.create"],
                    "MANAGER": ["quality.view", "quality.inspect", "quality.manage", "reports.create"],
                    "ADMIN": ["quality.*", "reports.*", "settings.*"]
                }
            },
            "abac": {
                "required": ["site", "department"],
                "optional": ["shift", "line"]
            },
            "pii_fields": ["inspector_name", "employee_id"],
            "data_classification": "internal",
            "encryption_required": True
        },
        
        "maintenance": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "TECHNICIAN", "SUPERVISOR", "ADMIN"],
                "permissions": {
                    "VIEWER": ["maintenance.view", "schedules.view"],
                    "TECHNICIAN": ["maintenance.view", "workorders.edit", "equipment.inspect"],
                    "SUPERVISOR": ["maintenance.*", "schedules.manage", "reports.create"],
                    "ADMIN": ["maintenance.*", "equipment.*", "settings.*"]
                }
            },
            "abac": {
                "required": ["site", "equipment_type"],
                "optional": ["shift", "certification_level"]
            },
            "pii_fields": ["technician_name", "employee_id"],
            "data_classification": "internal"
        },
        
        "safety": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "OFFICER", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["safety.view", "incidents.view"],
                    "OFFICER": ["safety.*", "incidents.create", "hazards.assess"],
                    "MANAGER": ["safety.*", "compliance.manage", "training.approve"],
                    "ADMIN": ["safety.*", "compliance.*", "settings.*"]
                }
            },
            "abac": {
                "required": ["site", "safety_zone"],
                "optional": ["clearance_level"]
            },
            "pii_fields": ["officer_name", "incident_witnesses"],
            "data_classification": "confidential"
        },
        
        "operations": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "OPERATOR", "SUPERVISOR", "ADMIN"],
                "permissions": {
                    "VIEWER": ["operations.view", "metrics.view"],
                    "OPERATOR": ["operations.view", "production.control", "data.entry"],
                    "SUPERVISOR": ["operations.*", "schedules.manage", "performance.analyze"],
                    "ADMIN": ["operations.*", "settings.*", "integration.*"]
                }
            },
            "abac": {
                "required": ["site", "production_line"],
                "optional": ["shift", "certification"]
            },
            "data_classification": "internal"
        },
        
        "finance": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "ANALYST", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["finance.view", "reports.view"],
                    "ANALYST": ["finance.view", "budgets.edit", "analysis.create"],
                    "MANAGER": ["finance.*", "approvals.manage", "forecasts.create"],
                    "ADMIN": ["finance.*", "settings.*", "audit.*"]
                }
            },
            "abac": {
                "required": ["cost_center", "region"],
                "optional": ["approval_limit"]
            },
            "pii_fields": ["employee_id", "vendor_info"],
            "data_classification": "confidential",
            "encryption_required": True
        },
        
        "marketing": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "COORDINATOR", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["campaigns.view", "analytics.view"],
                    "COORDINATOR": ["campaigns.edit", "content.create", "leads.manage"],
                    "MANAGER": ["campaigns.*", "budgets.manage", "strategy.plan"],
                    "ADMIN": ["marketing.*", "integrations.*", "settings.*"]
                }
            },
            "abac": {
                "required": ["department", "region"],
                "optional": ["campaign_access", "budget_level"]
            },
            "pii_fields": ["customer_data", "lead_info"],
            "data_classification": "internal"
        },
        
        "sales": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "REP", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["leads.view", "reports.view"],
                    "REP": ["leads.*", "opportunities.*", "activities.*"],
                    "MANAGER": ["sales.*", "territories.manage", "forecasts.create"],
                    "ADMIN": ["sales.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["territory", "region"],
                "optional": ["deal_limit", "discount_level"]
            },
            "pii_fields": ["customer_data", "contact_info"],
            "data_classification": "confidential"
        },
        
        "hr": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "COORDINATOR", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["employees.view", "org_chart.view"],
                    "COORDINATOR": ["employees.edit", "recruitment.manage", "training.coordinate"],
                    "MANAGER": ["hr.*", "performance.manage", "compensation.view"],
                    "ADMIN": ["hr.*", "payroll.*", "settings.*"]
                }
            },
            "abac": {
                "required": ["department", "clearance_level"],
                "optional": ["salary_access", "review_access"]
            },
            "pii_fields": ["employee_data", "ssn", "salary_info"],
            "data_classification": "confidential",
            "encryption_required": True
        },
        
        "legal": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "PARALEGAL", "ATTORNEY", "ADMIN"],
                "permissions": {
                    "VIEWER": ["documents.view", "matters.view"],
                    "PARALEGAL": ["documents.edit", "research.conduct", "billing.track"],
                    "ATTORNEY": ["legal.*", "matters.manage", "contracts.approve"],
                    "ADMIN": ["legal.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["practice_area", "clearance_level"],
                "optional": ["client_access", "matter_type"]
            },
            "pii_fields": ["client_data", "case_info"],
            "data_classification": "confidential",
            "encryption_required": True
        },
        
        "customer_success": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "CSM", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["customers.view", "health.view"],
                    "CSM": ["customers.*", "support.*", "training.deliver"],
                    "MANAGER": ["success.*", "programs.manage", "analytics.view"],
                    "ADMIN": ["success.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["region", "customer_tier"],
                "optional": ["support_level"]
            },
            "pii_fields": ["customer_data", "usage_data"],
            "data_classification": "internal"
        },
        
        "product": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "ANALYST", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["roadmap.view", "metrics.view"],
                    "ANALYST": ["research.conduct", "analysis.create", "feedback.analyze"],
                    "MANAGER": ["product.*", "roadmap.manage", "strategy.plan"],
                    "ADMIN": ["product.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["product_line", "region"],
                "optional": ["feature_access"]
            },
            "data_classification": "internal"
        },
        
        "chatterfix": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["VIEWER", "TECHNICIAN", "SUPERVISOR", "MANAGER", "ADMIN"],
                "permissions": {
                    "VIEWER": ["workorders.view", "assets.view"],
                    "TECHNICIAN": ["workorders.*", "maintenance.execute", "mobile.*"],
                    "SUPERVISOR": ["scheduling.*", "assignments.manage", "reports.view"],
                    "MANAGER": ["maintenance.*", "analytics.view", "budgets.manage"],
                    "ADMIN": ["chatterfix.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["site", "equipment_type"],
                "optional": ["shift", "certification_level", "mobile_device"]
            },
            "pii_fields": ["technician_name", "employee_id", "voice_recordings"],
            "data_classification": "internal",
            "voice_enabled": True,
            "offline_capable": True,
            "mobile_optimized": True
        },
        
        "linesmart": {
            "required_claims": ["tenant", "module", "roles"],
            "rbac": {
                "roles": ["LEARNER", "INSTRUCTOR", "COORDINATOR", "MANAGER", "ADMIN"],
                "permissions": {
                    "LEARNER": ["courses.view", "training.take", "progress.view"],
                    "INSTRUCTOR": ["content.create", "assessments.grade", "analytics.view"],
                    "COORDINATOR": ["training.manage", "employees.assign", "reports.create"],
                    "MANAGER": ["programs.manage", "analytics.*", "compliance.monitor"],
                    "ADMIN": ["linesmart.*", "settings.*", "integrations.*"]
                }
            },
            "abac": {
                "required": ["department", "training_level"],
                "optional": ["language_preference", "certification_type"]
            },
            "pii_fields": ["employee_data", "training_records", "assessment_results"],
            "data_classification": "internal",
            "multilingual": True,
            "rag_enabled": True,
            "ai_content_generation": True
        }
    }
    
    for module_name, config in modules.items():
        await ai_identity_core.register_module(module_name, config)

# Initialize the identity system
async def initialize_ai_identity():
    """Initialize AI Identity Core with all modules"""
    print("🔐 Initializing AI Identity Core...")
    await register_fixitfred_modules()
    print("✅ AI Identity Core ready with module authentication")

if __name__ == "__main__":
    asyncio.run(initialize_ai_identity())
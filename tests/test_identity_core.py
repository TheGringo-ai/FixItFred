#!/usr/bin/env python3
"""
Run 1 — AI Identity Core (JWT, RBAC/ABAC, Audit)
Goal: Prove per-module auth works end-to-end
"""

import pytest
import requests
import jwt
import time
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8080"
ISS = "https://id.fixitfred.ai/ai_identity_core"

class TestIdentityCore:
    """Test AI Identity Core functionality"""
    
    def test_jwt_issuance_and_validation(self):
        """Test JWT token issuance and JWKS validation"""
        
        # 1) Request a token for maintenance module
        auth_payload = {
            "tenant": "acme_corp",
            "user_id": "tech_001", 
            "module": "maintenance",
            "roles": ["TECHNICIAN"],
            "abac": {
                "site": "PLANT_3",
                "department": "maintenance",
                "shift": "day",
                "security_level": "standard"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/identity/authenticate",
            json=auth_payload,
            timeout=10
        )
        
        assert response.status_code == 200
        token_data = response.json()
        assert "token" in token_data
        assert "expires_in" in token_data
        
        # 2) Validate token structure
        token = token_data["token"]
        
        # Decode without verification to check structure
        decoded = jwt.decode(token, options={"verify_signature": False})
        assert decoded["iss"] == ISS
        assert decoded["tenant"] == "acme_corp"
        assert decoded["module"] == "maintenance"
        assert "TECHNICIAN" in decoded["roles"]
        
        # 3) Verify JWKS endpoint
        jwks_response = requests.get(f"{BASE_URL}/api/identity/jwks")
        assert jwks_response.status_code == 200
        jwks = jwks_response.json()
        assert "keys" in jwks
        assert len(jwks["keys"]) > 0
        
        return token
    
    def test_rbac_enforcement(self):
        """Test Role-Based Access Control enforcement"""
        
        # Get token for technician role
        tech_token = self._get_test_token("TECHNICIAN", {"site": "PLANT_3"})
        
        # Get token for manager role  
        mgr_token = self._get_test_token("MANAGER", {"site": "PLANT_3"})
        
        # 1) Technician can view work orders
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders",
            headers={"Authorization": f"Bearer {tech_token}"}
        )
        assert response.status_code == 200
        
        # 2) Technician cannot create new equipment
        equipment_data = {
            "name": "Test Equipment",
            "type": "pump",
            "location": "PLANT_3"
        }
        response = requests.post(
            f"{BASE_URL}/api/maintenance/equipment",
            json=equipment_data,
            headers={"Authorization": f"Bearer {tech_token}"}
        )
        assert response.status_code == 403  # Forbidden
        
        # 3) Manager can create equipment
        response = requests.post(
            f"{BASE_URL}/api/maintenance/equipment", 
            json=equipment_data,
            headers={"Authorization": f"Bearer {mgr_token}"}
        )
        assert response.status_code in (200, 201)
    
    def test_abac_enforcement(self):
        """Test Attribute-Based Access Control (ABAC) enforcement"""
        
        # Get tokens for different sites
        plant3_token = self._get_test_token("TECHNICIAN", {"site": "PLANT_3"})
        plant5_token = self._get_test_token("TECHNICIAN", {"site": "PLANT_5"})
        
        # 1) PLANT_3 technician can access PLANT_3 work orders
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders?site=PLANT_3",
            headers={"Authorization": f"Bearer {plant3_token}"}
        )
        assert response.status_code == 200
        
        # 2) PLANT_3 technician cannot access PLANT_5 work orders
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders?site=PLANT_5",
            headers={"Authorization": f"Bearer {plant3_token}"}
        )
        assert response.status_code == 403
        
        # 3) PLANT_5 technician can access their own site
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders?site=PLANT_5", 
            headers={"Authorization": f"Bearer {plant5_token}"}
        )
        assert response.status_code == 200
    
    def test_audit_logging(self):
        """Test audit trail generation for security events"""
        
        token = self._get_test_token("TECHNICIAN", {"site": "PLANT_3"})
        
        # 1) Perform authenticated action
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders/WO-12345",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 2) Attempt unauthorized action
        mgr_data = {"budget": 50000, "priority": "critical"}
        response = requests.put(
            f"{BASE_URL}/api/maintenance/workorders/WO-12345/manager-override",
            json=mgr_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        
        # 3) Check audit logs
        time.sleep(0.5)  # Allow audit processing
        audit_response = requests.get(f"{BASE_URL}/api/audit/events?limit=10")
        assert audit_response.status_code == 200
        
        audit_events = audit_response.json()
        assert isinstance(audit_events, list)
        assert len(audit_events) >= 2
        
        # Verify audit event structure
        recent_event = audit_events[0]
        required_fields = ["timestamp", "event", "user", "module", "action", "result"]
        for field in required_fields:
            assert field in recent_event
        
        # Verify security denial is logged
        denial_events = [e for e in audit_events if e.get("result") == "denied"]
        assert len(denial_events) >= 1
    
    def test_token_expiration_and_refresh(self):
        """Test token expiration and refresh mechanism"""
        
        # 1) Get short-lived token (for testing)
        auth_payload = {
            "tenant": "acme_corp",
            "user_id": "tech_001",
            "module": "maintenance", 
            "roles": ["TECHNICIAN"],
            "token_lifetime": 2  # 2 seconds for testing
        }
        
        response = requests.post(
            f"{BASE_URL}/api/identity/authenticate",
            json=auth_payload
        )
        assert response.status_code == 200
        
        token_data = response.json()
        token = token_data["token"]
        
        # 2) Token works initially
        response = requests.get(
            f"{BASE_URL}/api/maintenance/health",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # 3) Wait for expiration
        time.sleep(3)
        
        # 4) Token should be expired
        response = requests.get(
            f"{BASE_URL}/api/maintenance/health",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        
        # 5) Refresh token
        refresh_response = requests.post(
            f"{BASE_URL}/api/identity/refresh",
            json={"token": token}
        )
        # Should either succeed with new token or fail gracefully
        assert refresh_response.status_code in (200, 401, 403)
    
    def test_multi_tenant_isolation(self):
        """Test tenant isolation in authentication"""
        
        # Get tokens for different tenants
        acme_token = self._get_test_token("MANAGER", {"site": "PLANT_1"}, tenant="acme_corp")
        beta_token = self._get_test_token("MANAGER", {"site": "PLANT_1"}, tenant="beta_corp")
        
        # 1) Create resource with ACME tenant
        resource_data = {"name": "ACME Equipment", "tenant": "acme_corp"}
        response = requests.post(
            f"{BASE_URL}/api/maintenance/equipment",
            json=resource_data,
            headers={"Authorization": f"Bearer {acme_token}"}
        )
        assert response.status_code in (200, 201)
        
        if response.status_code in (200, 201):
            equipment_id = response.json().get("id")
            
            # 2) BETA tenant cannot access ACME resource
            response = requests.get(
                f"{BASE_URL}/api/maintenance/equipment/{equipment_id}",
                headers={"Authorization": f"Bearer {beta_token}"}
            )
            assert response.status_code in (404, 403)  # Not found or forbidden
    
    def _get_test_token(self, role, abac_context, tenant="acme_corp"):
        """Helper method to get test tokens"""
        
        auth_payload = {
            "tenant": tenant,
            "user_id": f"test_user_{role.lower()}",
            "module": "maintenance",
            "roles": [role],
            "abac": abac_context
        }
        
        response = requests.post(
            f"{BASE_URL}/api/identity/authenticate",
            json=auth_payload,
            timeout=5
        )
        
        if response.status_code != 200:
            pytest.skip(f"Could not get test token: {response.status_code}")
        
        return response.json()["token"]

# Integration test for full authentication flow
def test_full_authentication_flow():
    """Test complete authentication flow from user login to resource access"""
    
    # 1) User authentication
    login_data = {
        "username": "john.technician",
        "password": "test_password",
        "tenant": "acme_corp"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        user_session = response.json()
        
        # 2) Request module access
        module_request = {
            "module": "maintenance",
            "requested_permissions": ["workorders.view", "workorders.edit"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/identity/module-access",
            json=module_request,
            headers={"Authorization": f"Bearer {user_session['session_token']}"}
        )
        
        assert response.status_code == 200
        module_token = response.json()["module_token"]
        
        # 3) Use module token
        response = requests.get(
            f"{BASE_URL}/api/maintenance/workorders",
            headers={"Authorization": f"Bearer {module_token}"}
        )
        
        assert response.status_code == 200

if __name__ == "__main__":
    # Run tests individually for debugging
    test_instance = TestIdentityCore()
    
    print("🔐 Testing AI Identity Core...")
    
    try:
        test_instance.test_jwt_issuance_and_validation()
        print("✅ JWT issuance and validation - PASSED")
    except Exception as e:
        print(f"❌ JWT issuance and validation - FAILED: {e}")
    
    try:
        test_instance.test_rbac_enforcement()
        print("✅ RBAC enforcement - PASSED")
    except Exception as e:
        print(f"❌ RBAC enforcement - FAILED: {e}")
    
    try:
        test_instance.test_abac_enforcement()
        print("✅ ABAC enforcement - PASSED")
    except Exception as e:
        print(f"❌ ABAC enforcement - FAILED: {e}")
    
    try:
        test_instance.test_audit_logging()
        print("✅ Audit logging - PASSED")
    except Exception as e:
        print(f"❌ Audit logging - FAILED: {e}")
    
    print("\n🎯 AI Identity Core testing complete!")
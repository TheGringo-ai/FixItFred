#!/usr/bin/env python3
"""
FixItFred Universal Integration Hub
Connect any application, API, automation, or system during client onboarding
"""

import asyncio
import json
import uuid
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import base64
import hmac
import hashlib

@dataclass
class IntegrationEndpoint:
    """Define an integration endpoint"""
    id: str
    name: str
    type: str  # 'api', 'webhook', 'database', 'file', 'custom'
    url: str
    method: str = 'GET'  # GET, POST, PUT, DELETE, PATCH
    headers: Dict[str, str] = None
    auth_type: str = 'none'  # none, api_key, bearer, basic, oauth2, custom
    auth_config: Dict[str, Any] = None
    parameters: Dict[str, Any] = None
    data_format: str = 'json'  # json, xml, form, csv, custom
    frequency: str = 'on_demand'  # on_demand, hourly, daily, weekly, real_time
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.auth_config is None:
            self.auth_config = {}
        if self.parameters is None:
            self.parameters = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class DataMapping:
    """Map external data to FixItFred modules"""
    source_field: str
    target_module: str  # quality, maintenance, safety, operations, finance, hr
    target_field: str
    transformation: str = 'direct'  # direct, calculate, format, lookup, custom
    validation_rules: List[str] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []

@dataclass
class Integration:
    """Complete integration configuration"""
    id: str
    client_id: str
    name: str
    description: str
    system_type: str  # erp, crm, mes, plm, iot, automation, custom
    endpoints: List[IntegrationEndpoint]
    data_mappings: List[DataMapping]
    status: str = 'active'  # active, inactive, error, testing
    last_sync: datetime = None
    sync_count: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        if self.last_sync is None:
            self.last_sync = datetime.now()

class UniversalConnector:
    """Universal connector for any system integration"""
    
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self.supported_systems = {
            'erp': {
                'SAP': {'endpoints': ['/api/v1/data'], 'auth': 'oauth2'},
                'Oracle': {'endpoints': ['/api/data'], 'auth': 'basic'},
                'Microsoft Dynamics': {'endpoints': ['/api/dynamics'], 'auth': 'oauth2'},
                'NetSuite': {'endpoints': ['/rest/v1'], 'auth': 'oauth2'},
                'QuickBooks': {'endpoints': ['/v3/company'], 'auth': 'oauth2'}
            },
            'crm': {
                'Salesforce': {'endpoints': ['/services/data/v52.0'], 'auth': 'oauth2'},
                'HubSpot': {'endpoints': ['/api/v3'], 'auth': 'api_key'},
                'Pipedrive': {'endpoints': ['/v1'], 'auth': 'api_key'},
                'Zoho': {'endpoints': ['/crm/v2'], 'auth': 'oauth2'}
            },
            'mes': {
                'Wonderware': {'endpoints': ['/api/v1'], 'auth': 'basic'},
                'GE Proficy': {'endpoints': ['/api/data'], 'auth': 'custom'},
                'Siemens SIMATIC': {'endpoints': ['/webapi'], 'auth': 'basic'},
                'Rockwell FactoryTalk': {'endpoints': ['/api'], 'auth': 'basic'}
            },
            'iot': {
                'AWS IoT': {'endpoints': ['/topics'], 'auth': 'aws_sig'},
                'Azure IoT': {'endpoints': ['/devices'], 'auth': 'sas_token'},
                'Google Cloud IoT': {'endpoints': ['/devices'], 'auth': 'jwt'},
                'ThingWorx': {'endpoints': ['/Thingworx/Things'], 'auth': 'api_key'}
            },
            'automation': {
                'Zapier': {'endpoints': ['/webhooks'], 'auth': 'webhook'},
                'Microsoft Power Automate': {'endpoints': ['/triggers'], 'auth': 'oauth2'},
                'IFTTT': {'endpoints': ['/webhooks'], 'auth': 'webhook'},
                'Integromat/Make': {'endpoints': ['/webhooks'], 'auth': 'webhook'}
            }
        }
        
    async def create_integration(self, client_id: str, integration_config: Dict[str, Any]) -> Integration:
        """Create a new integration for a client"""
        
        integration_id = f"{client_id}_{integration_config['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Convert endpoint configurations to IntegrationEndpoint objects
        endpoints = []
        for ep_config in integration_config.get('endpoints', []):
            endpoint = IntegrationEndpoint(
                id=f"{integration_id}_ep_{len(endpoints)}",
                **ep_config
            )
            endpoints.append(endpoint)
        
        # Convert data mapping configurations
        data_mappings = []
        for dm_config in integration_config.get('data_mappings', []):
            mapping = DataMapping(**dm_config)
            data_mappings.append(mapping)
        
        integration = Integration(
            id=integration_id,
            client_id=client_id,
            name=integration_config['name'],
            description=integration_config.get('description', ''),
            system_type=integration_config.get('system_type', 'custom'),
            endpoints=endpoints,
            data_mappings=data_mappings
        )
        
        self.integrations[integration_id] = integration
        
        # Test the integration
        await self.test_integration(integration_id)
        
        return integration
    
    async def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test an integration to ensure it's working"""
        
        if integration_id not in self.integrations:
            return {"success": False, "error": "Integration not found"}
        
        integration = self.integrations[integration_id]
        test_results = []
        
        for endpoint in integration.endpoints:
            try:
                result = await self._test_endpoint(endpoint)
                test_results.append({
                    "endpoint": endpoint.name,
                    "success": result['success'],
                    "response_time": result['response_time'],
                    "status_code": result.get('status_code'),
                    "error": result.get('error')
                })
            except Exception as e:
                test_results.append({
                    "endpoint": endpoint.name,
                    "success": False,
                    "error": str(e)
                })
        
        overall_success = all(result['success'] for result in test_results)
        integration.status = 'active' if overall_success else 'error'
        
        return {
            "integration_id": integration_id,
            "overall_success": overall_success,
            "endpoint_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _test_endpoint(self, endpoint: IntegrationEndpoint) -> Dict[str, Any]:
        """Test a specific endpoint"""
        
        start_time = datetime.now()
        
        try:
            # Prepare headers
            headers = endpoint.headers.copy()
            
            # Add authentication
            auth_headers = await self._prepare_auth(endpoint)
            headers.update(auth_headers)
            
            # Make request
            if endpoint.method.upper() == 'GET':
                response = requests.get(
                    endpoint.url,
                    headers=headers,
                    params=endpoint.parameters,
                    timeout=30
                )
            elif endpoint.method.upper() == 'POST':
                response = requests.post(
                    endpoint.url,
                    headers=headers,
                    json=endpoint.parameters,
                    timeout=30
                )
            else:
                response = requests.request(
                    endpoint.method.upper(),
                    endpoint.url,
                    headers=headers,
                    timeout=30
                )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response_time,
                "data_preview": response.text[:200] if len(response.text) > 200 else response.text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": (datetime.now() - start_time).total_seconds() * 1000
            }
    
    async def _prepare_auth(self, endpoint: IntegrationEndpoint) -> Dict[str, str]:
        """Prepare authentication headers for endpoint"""
        
        headers = {}
        
        if endpoint.auth_type == 'api_key':
            api_key = endpoint.auth_config.get('api_key', '')
            key_location = endpoint.auth_config.get('location', 'header')  # header, query, body
            key_name = endpoint.auth_config.get('key_name', 'X-API-Key')
            
            if key_location == 'header':
                headers[key_name] = api_key
                
        elif endpoint.auth_type == 'bearer':
            token = endpoint.auth_config.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
            
        elif endpoint.auth_type == 'basic':
            username = endpoint.auth_config.get('username', '')
            password = endpoint.auth_config.get('password', '')
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
            
        elif endpoint.auth_type == 'oauth2':
            access_token = endpoint.auth_config.get('access_token', '')
            headers['Authorization'] = f'Bearer {access_token}'
            
        return headers
    
    async def sync_data(self, integration_id: str) -> Dict[str, Any]:
        """Sync data from external system"""
        
        if integration_id not in self.integrations:
            return {"success": False, "error": "Integration not found"}
        
        integration = self.integrations[integration_id]
        sync_results = []
        total_records = 0
        
        for endpoint in integration.endpoints:
            try:
                # Fetch data from endpoint
                data = await self._fetch_endpoint_data(endpoint)
                
                # Process and map data
                mapped_data = await self._map_data(data, integration.data_mappings)
                
                # Store data in appropriate modules
                storage_result = await self._store_mapped_data(mapped_data, integration.client_id)
                
                sync_results.append({
                    "endpoint": endpoint.name,
                    "success": True,
                    "records_processed": len(mapped_data),
                    "storage_result": storage_result
                })
                
                total_records += len(mapped_data)
                
            except Exception as e:
                sync_results.append({
                    "endpoint": endpoint.name,
                    "success": False,
                    "error": str(e)
                })
        
        # Update integration statistics
        integration.last_sync = datetime.now()
        integration.sync_count += 1
        
        return {
            "integration_id": integration_id,
            "total_records": total_records,
            "endpoint_results": sync_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _fetch_endpoint_data(self, endpoint: IntegrationEndpoint) -> List[Dict[str, Any]]:
        """Fetch data from an endpoint"""
        
        headers = endpoint.headers.copy()
        auth_headers = await self._prepare_auth(endpoint)
        headers.update(auth_headers)
        
        response = requests.get(
            endpoint.url,
            headers=headers,
            params=endpoint.parameters,
            timeout=60
        )
        
        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        if endpoint.data_format == 'json':
            data = response.json()
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Look for common data containers
                for key in ['data', 'results', 'items', 'records']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data]  # Single record
            else:
                return [{"raw_data": data}]
        else:
            # Handle other formats (CSV, XML, etc.)
            return [{"raw_data": response.text}]
    
    async def _map_data(self, raw_data: List[Dict[str, Any]], mappings: List[DataMapping]) -> List[Dict[str, Any]]:
        """Map raw data to FixItFred module format"""
        
        mapped_records = []
        
        for record in raw_data:
            mapped_record = {"raw_data": record}
            
            for mapping in mappings:
                if mapping.source_field in record:
                    source_value = record[mapping.source_field]
                    
                    # Apply transformation
                    if mapping.transformation == 'direct':
                        mapped_value = source_value
                    elif mapping.transformation == 'calculate':
                        # Simple calculation example
                        mapped_value = float(source_value) * 1.0 if isinstance(source_value, (int, float, str)) else source_value
                    elif mapping.transformation == 'format':
                        mapped_value = str(source_value).strip().upper()
                    else:
                        mapped_value = source_value
                    
                    mapped_record[f"{mapping.target_module}_{mapping.target_field}"] = mapped_value
            
            mapped_records.append(mapped_record)
        
        return mapped_records
    
    async def _store_mapped_data(self, mapped_data: List[Dict[str, Any]], client_id: str) -> Dict[str, Any]:
        """Store mapped data in appropriate FixItFred modules"""
        
        # This would integrate with your actual data storage system
        # For now, we'll simulate storage
        
        modules_affected = set()
        for record in mapped_data:
            for key in record.keys():
                if '_' in key and not key.startswith('raw_'):
                    module = key.split('_')[0]
                    modules_affected.add(module)
        
        return {
            "success": True,
            "records_stored": len(mapped_data),
            "modules_affected": list(modules_affected),
            "client_id": client_id
        }
    
    async def get_integration_templates(self) -> Dict[str, Any]:
        """Get pre-built integration templates for common systems"""
        
        templates = {}
        
        for system_type, systems in self.supported_systems.items():
            templates[system_type] = {}
            for system_name, config in systems.items():
                templates[system_type][system_name] = {
                    "name": system_name,
                    "type": system_type,
                    "auth_type": config['auth'],
                    "endpoints": config['endpoints'],
                    "common_mappings": self._get_common_mappings(system_type),
                    "setup_instructions": self._get_setup_instructions(system_name)
                }
        
        return templates
    
    def _get_common_mappings(self, system_type: str) -> List[Dict[str, str]]:
        """Get common data mappings for system type"""
        
        mappings = {
            'erp': [
                {"source_field": "item_id", "target_module": "quality", "target_field": "product_id"},
                {"source_field": "quantity", "target_module": "operations", "target_field": "production_quantity"},
                {"source_field": "cost", "target_module": "finance", "target_field": "unit_cost"}
            ],
            'mes': [
                {"source_field": "machine_id", "target_module": "maintenance", "target_field": "equipment_id"},
                {"source_field": "status", "target_module": "operations", "target_field": "machine_status"},
                {"source_field": "production_rate", "target_module": "operations", "target_field": "efficiency"}
            ],
            'iot': [
                {"source_field": "sensor_value", "target_module": "maintenance", "target_field": "sensor_reading"},
                {"source_field": "timestamp", "target_module": "operations", "target_field": "measurement_time"},
                {"source_field": "alert_level", "target_module": "safety", "target_field": "risk_level"}
            ]
        }
        
        return mappings.get(system_type, [])
    
    def _get_setup_instructions(self, system_name: str) -> List[str]:
        """Get setup instructions for specific systems"""
        
        instructions = {
            'SAP': [
                "1. Enable SAP OData services",
                "2. Create service user with appropriate permissions",
                "3. Generate OAuth2 client credentials",
                "4. Configure SSL certificate if required"
            ],
            'Salesforce': [
                "1. Create Connected App in Salesforce",
                "2. Enable OAuth settings and API access",
                "3. Note Consumer Key and Consumer Secret",
                "4. Generate refresh token for authentication"
            ],
            'Zapier': [
                "1. Create new Zap in Zapier",
                "2. Set trigger as 'Webhooks by Zapier'",
                "3. Copy webhook URL provided",
                "4. Configure trigger event and data format"
            ]
        }
        
        return instructions.get(system_name, [
            "1. Obtain API credentials from system administrator",
            "2. Identify API endpoints for data access",
            "3. Configure authentication method",
            "4. Test connection and data format"
        ])
    
    async def create_webhook_endpoint(self, integration_id: str, webhook_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a webhook endpoint for real-time data"""
        
        webhook_id = f"webhook_{integration_id}_{uuid.uuid4().hex[:8]}"
        webhook_url = f"https://your-domain.com/api/webhooks/{webhook_id}"
        
        # This would create actual webhook endpoint in your system
        webhook_endpoint = {
            "id": webhook_id,
            "integration_id": integration_id,
            "url": webhook_url,
            "secret": uuid.uuid4().hex,
            "events": webhook_config.get('events', ['*']),
            "headers": webhook_config.get('headers', {}),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        return webhook_endpoint
    
    async def get_client_integrations(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all integrations for a client"""
        
        client_integrations = []
        
        for integration in self.integrations.values():
            if integration.client_id == client_id:
                integration_data = asdict(integration)
                integration_data['endpoints'] = [asdict(ep) for ep in integration.endpoints]
                integration_data['data_mappings'] = [asdict(dm) for dm in integration.data_mappings]
                client_integrations.append(integration_data)
        
        return client_integrations

# Global universal connector instance
universal_connector = UniversalConnector()
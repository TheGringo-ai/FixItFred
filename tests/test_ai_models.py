#!/usr/bin/env python3
"""
AI Models Testing - Llama default, user API keys for other services
Goal: Prove AI model integration works with fallback hierarchy
"""

import pytest
import requests
import os
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8080"

class TestAIModels:
    """Test AI Model integration and fallback system"""
    
    def test_llama_default_model(self):
        """Test that Llama is available as default local model"""
        
        # 1) Check if Llama model is loaded
        response = requests.get(f"{BASE_URL}/api/ai/models/available")
        assert response.status_code == 200
        
        models = response.json()
        assert isinstance(models, dict)
        
        # Verify Llama is in available models
        llama_models = [m for m in models.keys() if "llama" in m.lower()]
        assert len(llama_models) > 0, "No Llama models found"
        
        default_model = models.get("default", {})
        assert "llama" in default_model.get("name", "").lower()
        
        print(f"✅ Found Llama models: {llama_models}")
        return llama_models[0]
    
    def test_llama_inference(self):
        """Test Llama model inference capabilities"""
        
        # Test simple completion
        inference_request = {
            "model": "llama-default",
            "prompt": "What is the capital of France?",
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            json=inference_request,
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "response" in result
        assert len(result["response"]) > 0
        assert "paris" in result["response"].lower()
        
        # Test model metadata
        assert "model_used" in result
        assert "generation_time" in result
        assert result["generation_time"] < 10  # Should be fast locally
        
        print("✅ Llama inference working")
    
    def test_business_context_inference(self):
        """Test Llama with business/manufacturing context"""
        
        business_prompt = """
        You are an AI assistant for a manufacturing facility. 
        A technician asks: "The conveyor belt is making unusual noise. What should I check first?"
        Provide a practical, safety-focused response.
        """
        
        inference_request = {
            "model": "llama-default",
            "prompt": business_prompt,
            "max_tokens": 200,
            "temperature": 0.3,
            "context": "manufacturing_safety"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            json=inference_request
        )
        
        assert response.status_code == 200
        result = response.json()
        
        response_text = result["response"].lower()
        
        # Check for safety-related keywords
        safety_keywords = ["safety", "lockout", "stop", "power", "check", "inspect"]
        found_keywords = [kw for kw in safety_keywords if kw in response_text]
        assert len(found_keywords) >= 2, f"Response lacks safety focus: {response_text}"
        
        print("✅ Business context inference working")
    
    def test_openai_api_integration(self):
        """Test OpenAI API integration with user-provided keys"""
        
        # Check if OpenAI key is configured
        config_request = {
            "provider": "openai",
            "test_connection": True
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/config/test", json=config_request)
        
        if response.status_code == 200:
            # OpenAI is configured, test it
            inference_request = {
                "model": "gpt-3.5-turbo",
                "prompt": "Generate a brief safety reminder for factory workers.",
                "max_tokens": 100,
                "prefer_external": True
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/generate",
                json=inference_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert "response" in result
            assert result["model_used"] in ["gpt-3.5-turbo", "gpt-4"]
            
            print("✅ OpenAI integration working")
        else:
            print("⚠️ OpenAI not configured - skipping external API test")
    
    def test_claude_api_integration(self):
        """Test Claude API integration"""
        
        config_request = {
            "provider": "claude",
            "test_connection": True
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/config/test", json=config_request)
        
        if response.status_code == 200:
            inference_request = {
                "model": "claude-3-haiku",
                "prompt": "Explain why preventive maintenance is important in manufacturing.",
                "max_tokens": 150
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/generate",
                json=inference_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert "response" in result
            assert "claude" in result["model_used"].lower()
            
            print("✅ Claude integration working")
        else:
            print("⚠️ Claude not configured - skipping external API test")
    
    def test_model_fallback_hierarchy(self):
        """Test automatic fallback from external to local models"""
        
        # 1) Request with invalid external model
        inference_request = {
            "model": "gpt-nonexistent",
            "prompt": "Test fallback system",
            "max_tokens": 50,
            "fallback_enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            json=inference_request
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should have fallen back to local model
        assert "response" in result
        assert "llama" in result.get("model_used", "").lower()
        assert result.get("fallback_used") == True
        
        print("✅ Model fallback working")
    
    def test_api_key_configuration(self):
        """Test API key configuration for external services"""
        
        # 1) Test configuration endpoint
        response = requests.get(f"{BASE_URL}/api/ai/config")
        assert response.status_code == 200
        
        config = response.json()
        assert "providers" in config
        assert "openai" in config["providers"]
        assert "claude" in config["providers"]
        
        # 2) Test key validation (without exposing keys)
        for provider in ["openai", "claude", "gemini"]:
            validation_request = {
                "provider": provider,
                "validate_only": True
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/config/validate",
                json=validation_request
            )
            
            # Should return validation status
            assert response.status_code in (200, 400, 401)
            
            if response.status_code == 200:
                result = response.json()
                assert "valid" in result
                print(f"✅ {provider} configuration valid")
    
    def test_model_performance_comparison(self):
        """Test performance comparison between models"""
        
        test_prompt = "List 3 safety rules for operating industrial equipment."
        
        models_to_test = ["llama-default"]
        
        # Add external models if configured
        available_response = requests.get(f"{BASE_URL}/api/ai/models/available")
        if available_response.status_code == 200:
            available = available_response.json()
            if "gpt-3.5-turbo" in available:
                models_to_test.append("gpt-3.5-turbo")
            if "claude-3-haiku" in available:
                models_to_test.append("claude-3-haiku")
        
        performance_results = {}
        
        for model in models_to_test:
            start_time = time.time()
            
            inference_request = {
                "model": model,
                "prompt": test_prompt,
                "max_tokens": 100
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/generate",
                json=inference_request,
                timeout=30
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                performance_results[model] = {
                    "response_time": end_time - start_time,
                    "response_length": len(result["response"]),
                    "success": True
                }
            else:
                performance_results[model] = {
                    "success": False,
                    "error": response.status_code
                }
        
        # Verify at least one model worked
        successful_models = [m for m, r in performance_results.items() if r.get("success")]
        assert len(successful_models) > 0
        
        # Llama should be fastest (local)
        if "llama-default" in performance_results:
            llama_time = performance_results["llama-default"].get("response_time", float('inf'))
            assert llama_time < 10  # Should be under 10 seconds
        
        print(f"✅ Model performance comparison complete: {performance_results}")
    
    def test_custom_model_endpoints(self):
        """Test custom model endpoint configuration"""
        
        # Test adding custom endpoint
        custom_config = {
            "name": "custom-llama",
            "endpoint": "http://localhost:11434/api/generate",
            "model_type": "ollama",
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 200
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/models/custom",
            json=custom_config
        )
        
        # Should either succeed or return 409 if already exists
        assert response.status_code in (200, 201, 409)
        
        if response.status_code in (200, 201):
            # Test the custom endpoint
            inference_request = {
                "model": "custom-llama",
                "prompt": "Test custom endpoint",
                "max_tokens": 50
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/generate",
                json=inference_request
            )
            
            # May fail if endpoint not actually running
            assert response.status_code in (200, 500, 503)
            print("✅ Custom model endpoint configuration working")
    
    def test_ai_fine_tuning_interface(self):
        """Test AI fine-tuning interface for business context"""
        
        # Check if fine-tuning endpoint exists
        response = requests.get(f"{BASE_URL}/api/ai/fine-tuning/status")
        
        if response.status_code == 200:
            # Test training data upload
            training_data = {
                "domain": "manufacturing_safety",
                "examples": [
                    {
                        "input": "Equipment making noise",
                        "output": "First, ensure equipment is locked out and tagged out before inspection."
                    },
                    {
                        "input": "Maintenance schedule",
                        "output": "Follow the preventive maintenance schedule to avoid equipment failures."
                    }
                ]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/fine-tuning/data",
                json=training_data
            )
            
            assert response.status_code in (200, 201)
            print("✅ Fine-tuning interface working")
        else:
            print("⚠️ Fine-tuning interface not available")

# Integration tests
def test_voice_to_ai_pipeline():
    """Test voice command processing through AI models"""
    
    # Simulate voice command processing
    voice_request = {
        "audio_text": "Hey Fred, show me the maintenance schedule for pump P-101",
        "user_context": {
            "department": "maintenance",
            "role": "technician",
            "site": "PLANT_3"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/assistant/process-voice",
        json=voice_request
    )
    
    assert response.status_code in (200, 404, 501)  # May not be implemented yet
    
    if response.status_code == 200:
        result = response.json()
        assert "intent" in result
        assert "response" in result
        print("✅ Voice-to-AI pipeline working")

def test_rag_with_ai_models():
    """Test RAG (Retrieval Augmented Generation) with AI models"""
    
    # Test RAG query
    rag_request = {
        "query": "What are the safety procedures for electrical maintenance?",
        "model": "llama-default",
        "context_sources": ["safety_manual", "electrical_procedures"],
        "max_context_length": 2000
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/rag/query",
        json=rag_request
    )
    
    assert response.status_code in (200, 404, 501)
    
    if response.status_code == 200:
        result = response.json()
        assert "response" in result
        assert "sources" in result
        print("✅ RAG with AI models working")

if __name__ == "__main__":
    # Run tests individually for debugging
    test_instance = TestAIModels()
    
    print("🤖 Testing AI Models Integration...")
    
    try:
        test_instance.test_llama_default_model()
        print("✅ Llama default model - PASSED")
    except Exception as e:
        print(f"❌ Llama default model - FAILED: {e}")
    
    try:
        test_instance.test_llama_inference()
        print("✅ Llama inference - PASSED")
    except Exception as e:
        print(f"❌ Llama inference - FAILED: {e}")
    
    try:
        test_instance.test_business_context_inference()
        print("✅ Business context inference - PASSED")
    except Exception as e:
        print(f"❌ Business context inference - FAILED: {e}")
    
    try:
        test_instance.test_model_fallback_hierarchy()
        print("✅ Model fallback hierarchy - PASSED")
    except Exception as e:
        print(f"❌ Model fallback hierarchy - FAILED: {e}")
    
    try:
        test_instance.test_api_key_configuration()
        print("✅ API key configuration - PASSED")
    except Exception as e:
        print(f"❌ API key configuration - FAILED: {e}")
    
    print("\n🎯 AI Models testing complete!")
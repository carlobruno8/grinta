#!/usr/bin/env python3
"""Quick test to verify Gemini integration works.

This script tests the basic configuration and client setup without making API calls.
"""
import sys
import os

def test_imports():
    """Test that all necessary imports work."""
    print("✓ Testing imports...")
    try:
        import google.generativeai as genai
        print("  ✓ google.generativeai imported")
        
        from config import GrintaConfig, get_config
        print("  ✓ config imported")
        
        from reasoning.client import ReasoningClient, create_reasoning_client
        print("  ✓ reasoning.client imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration with mock API key."""
    print("\n✓ Testing configuration...")
    try:
        from config import GrintaConfig
        
        # Test with mock API key
        config = GrintaConfig(
            api_key="test-key-123",
            model="gemini-1.5-flash",
            temperature=0.0
        )
        
        assert config.api_key == "test-key-123"
        assert config.model == "gemini-1.5-flash"
        assert config.temperature == 0.0
        print("  ✓ Configuration object created successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False


def test_client_initialization():
    """Test client initialization with mock config."""
    print("\n✓ Testing client initialization...")
    try:
        from reasoning.client import ReasoningClient
        from config import GrintaConfig
        
        # Mock config
        config = GrintaConfig(
            api_key="test-key-123",
            model="gemini-1.5-flash"
        )
        
        # Initialize client
        client = ReasoningClient(config)
        
        assert client.config.api_key == "test-key-123"
        assert client.total_tokens_used == 0
        print("  ✓ Client initialized successfully")
        
        # Test token usage methods
        usage = client.get_token_usage()
        assert usage["total_tokens"] == 0
        print("  ✓ Token tracking works")
        
        return True
    except Exception as e:
        print(f"  ✗ Client test failed: {e}")
        return False


def test_schema_conversion():
    """Test JSON schema conversion for Gemini."""
    print("\n✓ Testing schema conversion...")
    try:
        from reasoning.client import ReasoningClient
        from config import GrintaConfig
        from reasoning.output_schema import EXPLANATION_JSON_SCHEMA
        
        config = GrintaConfig(api_key="test-key")
        client = ReasoningClient(config)
        
        # Test schema conversion
        gemini_schema = client._convert_schema_for_gemini(EXPLANATION_JSON_SCHEMA)
        
        assert "type" in gemini_schema
        assert "properties" in gemini_schema
        print("  ✓ Schema conversion works")
        
        return True
    except Exception as e:
        print(f"  ✗ Schema test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("GEMINI INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Client Init", test_client_initialization()))
    results.append(("Schema Conversion", test_schema_conversion()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Gemini integration is ready.")
        print("\nNext steps:")
        print("1. Set your GOOGLE_API_KEY environment variable")
        print("2. Run: pytest tests/test_reasoning.py -v")
        print("3. Run integration test: pytest tests/test_reasoning.py --run-integration")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

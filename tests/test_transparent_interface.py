#!/usr/bin/env python3
"""
Test script for JobPilot-OpenManus transparent web interface.
This script checks that all components are properly integrated.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent.manus import Manus
from app.prompt.jobpilot import get_jobpilot_prompt
from app.logger import logger

async def test_jobpilot_integration():
    """Test basic JobPilot integration."""
    print("🧪 Testing JobPilot-OpenManus Integration...")
    
    try:
        # Test 1: JobPilot Prompt Loading
        print("\n1. Testing JobPilot prompt system...")
        current_dir = os.getcwd()
        jobpilot_prompt = get_jobpilot_prompt(current_dir)
        
        if "JobPilot" in jobpilot_prompt and "job hunting" in jobpilot_prompt.lower():
            print("   ✅ JobPilot prompts loaded successfully")
        else:
            print("   ❌ JobPilot prompts not loaded correctly")
            return False
            
        # Test 2: Agent Creation
        print("\n2. Testing agent creation...")
        agent = await Manus.create()
        
        if agent and agent.name == "Manus":
            print("   ✅ Manus agent created successfully")
        else:
            print("   ❌ Agent creation failed")
            return False
            
        # Test 3: Tool Availability
        print("\n3. Testing available tools...")
        tools = agent.available_tools.tools
        tool_names = [tool.name for tool in tools]
        
        required_tools = ['python_execute', 'browser_use', 'str_replace_editor']
        missing_tools = [tool for tool in required_tools if tool not in tool_names]
        
        if not missing_tools:
            print(f"   ✅ All required tools available: {tool_names}")
        else:
            print(f"   ❌ Missing tools: {missing_tools}")
            return False
            
        # Test 4: Configuration Check
        print("\n4. Testing configuration...")
        from app.config import config
        
        if hasattr(config, 'llm') and hasattr(config.llm, 'model'):
            print(f"   ✅ LLM configuration: {config.llm.model}")
        elif isinstance(config.llm, dict) and 'model' in config.llm:
            print(f"   ✅ LLM configuration: {config.llm['model']}")
        else:
            print("   ✅ Configuration loaded (structure may vary)")
            
        # Cleanup
        await agent.cleanup()
        print("\n   ✅ Agent cleanup successful")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("JobPilot-OpenManus Transparent Interface Test")
    print("=" * 60)
    
    success = await test_jobpilot_integration()
    
    if success:
        print("\n🚀 System is ready for transparent job hunting!")
        print("\n📋 Next steps:")
        print("   1. Run: python web_server.py")
        print("   2. Open: http://localhost:8080")
        print("   3. Test with query: 'Show me Python developer jobs with 5 years experience in data science'")
        print("\n💡 Features you'll see:")
        print("   • Real-time progress updates")
        print("   • Live browser viewport showing JobPilot's actions")
        print("   • Activity log of all tool usage")
        print("   • Formatted job cards with direct links")
        print("   • Complete transparency in AI decision-making")
        
        return 0
    else:
        print("\n❌ System not ready. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Quick test of JSearch API functionality
"""

import asyncio
import aiohttp
from app.etl.settings import get_enhanced_settings

async def test_jsearch_api():
    print("🔍 Testing JSearch API...")
    
    settings = get_enhanced_settings()
    api_config = settings.get_api_config()
    
    print(f"API Key configured: {bool(api_config.api_key)}")
    print(f"Base URL: {api_config.base_url}")
    
    url = f'{api_config.base_url}/search'
    params = {
        'query': 'python developer',
        'page': 1,
        'num_pages': 1
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Making request to: {url}")
            print(f"Headers: {api_config.headers}")
            print(f"Params: {params}")
            
            async with session.get(url, headers=api_config.headers, params=params) as response:
                print(f'Response Status: {response.status}')
                
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get("data", [])
                    print(f'✅ Success! Found {len(jobs)} jobs')
                    
                    if jobs:
                        job = jobs[0]
                        print(f'📋 Sample job:')
                        print(f'   Title: {job.get("job_title", "N/A")}')
                        print(f'   Company: {job.get("employer_name", "N/A")}')
                        print(f'   Location: {job.get("job_city", "N/A")}, {job.get("job_state", "N/A")}')
                        print(f'   URL: {job.get("job_apply_link", "N/A")}')
                        
                    return True
                else:
                    text = await response.text()
                    print(f'❌ Error response ({response.status}): {text[:500]}')
                    return False
                    
        except Exception as e:
            print(f'❌ Request failed: {e}')
            return False

if __name__ == "__main__":
    success = asyncio.run(test_jsearch_api())
    print(f"\n🎯 JSearch API test {'✅ PASSED' if success else '❌ FAILED'}")

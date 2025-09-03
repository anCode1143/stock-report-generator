#!/usr/bin/env python3
"""
Simple script to test if your Google AI API key is working correctly.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_api_key():
    """Test if the Google AI API key is working"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to load .env from current directory
    dotenv_path = os.path.join(script_dir, '.env')
    
    print(f"📁 Looking for .env file at: {dotenv_path}")
    
    if os.path.exists(dotenv_path):
        print("✅ Found .env file")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print("❌ No .env file found - trying default location")
        load_dotenv()
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not api_key:
        print("❌ No API key found in environment variables")
        print("\n🔧 Setup Instructions:")
        print("1. Create a .env file in the project root")
        print("2. Add: GOOGLE_AI_API_KEY=your_actual_api_key")
        print("3. Get API key from: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"🔑 Testing API key: {api_key[:15]}...{api_key[-10:]}")
    print(f"🔑 Key length: {len(api_key)} characters")
    
    # Check for common issues
    if len(api_key) < 30:
        print("⚠️  Warning: API key seems too short")
    if api_key.startswith('"') or api_key.endswith('"'):
        print("⚠️  Warning: API key has quotes - removing them")
        api_key = api_key.strip('"')
    if ' ' in api_key:
        print("⚠️  Warning: API key contains spaces")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key.strip())
        
        # Try to list models
        print("🔍 Testing API connection...")
        models = list(genai.list_models())
        print(f"✅ API key works! Found {len(models)} available models:")
        
        for model in models[:5]:  # Show first 5 models
            print(f"  • {model.name}")
        
        # Try a simple generation test
        print("\n🤖 Testing simple generation...")
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content("Say hello in one word")
        print(f"✅ Simple test response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have credits/quota available")
        print("3. Verify the API key is enabled for Gemini API")
        print("4. Get a new API key from: https://aistudio.google.com/app/apikey")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google AI API Key...")
    print("=" * 50)
    
    success = test_api_key()
    
    print("=" * 50)
    if success:
        print("🎉 API key test PASSED! You can now run gemini_report.py")
    else:
        print("❌ API key test FAILED! Please fix the issues above")

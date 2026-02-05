#!/usr/bin/env python3
"""
Verify that all required API credentials and dependencies are properly configured
"""

import os
import sys
from dotenv import load_dotenv


def check_env_var(var_name: str, required: bool = True) -> bool:
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    if value:
        print(f"✅ {var_name}: Set")
        return True
    else:
        if required:
            print(f"❌ {var_name}: Not set (Required)")
        else:
            print(f"⚠️  {var_name}: Not set (Optional)")
        return not required


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists"""
    if file_path and os.path.exists(file_path):
        print(f"✅ {description}: Found at {file_path}")
        return True
    else:
        print(f"❌ {description}: Not found at {file_path}")
        return False


def check_import(module_name: str, package_name: str = None) -> bool:
    """Check if a Python package can be imported"""
    try:
        __import__(module_name)
        display_name = package_name or module_name
        print(f"✅ {display_name}: Installed")
        return True
    except ImportError:
        display_name = package_name or module_name
        print(f"❌ {display_name}: Not installed")
        return False


def main():
    """Main verification function"""
    print("=" * 80)
    print("  Interview Transcription Summary System - Setup Verification")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()

    all_checks_passed = True

    # Check environment variables
    print("📋 Checking Environment Variables...")
    print("-" * 80)

    all_checks_passed &= check_env_var("FIREFLIES_API_KEY", required=True)
    all_checks_passed &= check_env_var("ANTHROPIC_API_KEY", required=True)
    all_checks_passed &= check_env_var("GOOGLE_CREDENTIALS_PATH", required=False)

    print()

    # Check Google credentials file
    if os.getenv("GOOGLE_CREDENTIALS_PATH"):
        print("📁 Checking Google Credentials File...")
        print("-" * 80)
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        all_checks_passed &= check_file_exists(credentials_path, "Google Credentials JSON")
        print()

    # Check Python dependencies
    print("🐍 Checking Python Dependencies...")
    print("-" * 80)

    dependencies = [
        ("anthropic", "anthropic"),
        ("requests", "requests"),
        ("google.auth", "google-auth"),
        ("google.oauth2", "google-auth-oauthlib"),
        ("googleapiclient", "google-api-python-client"),
        ("dotenv", "python-dotenv"),
        ("tiktoken", "tiktoken"),
    ]

    for module, package in dependencies:
        all_checks_passed &= check_import(module, package)

    print()

    # Test API connections
    print("🔌 Testing API Connections...")
    print("-" * 80)

    # Test Fireflies
    try:
        from src.fireflies_client import FirefliesClient
        fireflies = FirefliesClient()
        print("✅ Fireflies API: Connected")
    except Exception as e:
        print(f"❌ Fireflies API: Connection failed - {e}")
        all_checks_passed = False

    # Test Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Simple test call
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("✅ Anthropic Claude API: Connected")
    except Exception as e:
        print(f"❌ Anthropic Claude API: Connection failed - {e}")
        all_checks_passed = False

    # Test Google Docs (if configured)
    if os.getenv("GOOGLE_CREDENTIALS_PATH"):
        try:
            from src.google_docs_client import GoogleDocsClient
            google_docs = GoogleDocsClient()
            print("✅ Google Docs API: Connected")
        except Exception as e:
            print(f"⚠️  Google Docs API: Connection failed - {e}")
            print("   (This is optional and won't prevent the system from working)")

    print()

    # Final summary
    print("=" * 80)
    if all_checks_passed:
        print("✅ All required checks passed! Your system is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run: python src/main.py --list-transcripts")
        print("  2. Or: python src/main.py --transcript-id <YOUR_ID>")
        print("=" * 80)
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("  1. Make sure you've created a .env file from .env.example")
        print("  2. Add your API keys to the .env file")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. For Google Docs setup: python src/main.py --setup-google")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())

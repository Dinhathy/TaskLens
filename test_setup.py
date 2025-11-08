"""
Quick setup validation script for TaskLens backend.
Run this to verify your environment is configured correctly.
"""
import sys
import os


def check_python_version():
    """Check Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.9+ required.")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_dependencies():
    """Check required packages are installed"""
    required = ['fastapi', 'uvicorn', 'pydantic', 'httpx', 'pydantic_settings']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} NOT installed")

    if missing:
        print(f"\nInstall missing packages with: pip install {' '.join(missing)}")
        return False
    return True


def check_env_file():
    """Check .env file exists and has API key"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create it with: copy .env.example .env")
        return False

    print("✓ .env file exists")

    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('NVIDIA_API_KEY', '')
    if not api_key or api_key == 'your_nvidia_api_key_here':
        print("⚠️  NVIDIA_API_KEY not configured in .env")
        print("   Add your API key from https://build.nvidia.com/")
        return False

    print("✓ NVIDIA_API_KEY configured")
    return True


def check_imports():
    """Check all project modules can be imported"""
    try:
        from schemas import TaskRequest, TaskPlan, PLAN_SCHEMA
        print("✓ schemas.py imports successfully")

        from config import get_settings
        print("✓ config.py imports successfully")

        from services import NemotronService
        print("✓ services.py imports successfully")

        from main import app
        print("✓ main.py imports successfully")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Run all checks"""
    print("TaskLens Backend Setup Validation")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Module Imports", check_imports)
    ]

    results = []
    for name, check in checks:
        print(f"\n{name}:")
        results.append(check())

    print("\n" + "=" * 50)
    if all(results):
        print("✓ All checks passed! You're ready to run the server.")
        print("\nStart the server with:")
        print("  uvicorn main:app --reload")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

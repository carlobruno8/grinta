#!/usr/bin/env python3
"""Convenience script to run the Grinta Streamlit app."""
import os
import subprocess
import sys
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Path to the main app
app_path = project_root / "app" / "main.py"

if not app_path.exists():
    print(f"❌ Error: App file not found at {app_path}")
    sys.exit(1)

print("🚀 Starting Grinta Streamlit app...")
print(f"📁 Project root: {project_root}")
print(f"🎯 App path: {app_path}")
print()

# Run streamlit using python -m to avoid PATH issues
try:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        check=True,
    )
except KeyboardInterrupt:
    print("\n👋 App stopped")
except subprocess.CalledProcessError as e:
    print(f"❌ Error running app: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry running manually:")
    print(f"   {sys.executable} -m streamlit run app/main.py")
    sys.exit(1)

#!/usr/bin/env python3
"""
Chess Vision Live - Application Launcher

This script sets up the proper Python path and launches the application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set working directory to project root
os.chdir(project_root)

if __name__ == "__main__":
    # Import and run the UI
    from ui.app import create_ui
    
    print("🎯 Starting Chess Vision Live...")
    print(f"📁 Project root: {project_root}")
    print("🌐 Launching web interface...")
    
    demo = create_ui()
    demo.launch(
    )



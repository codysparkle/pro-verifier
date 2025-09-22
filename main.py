#!/usr/bin/env python3
"""
Social Profile Verification Tool
Entry point for running the verification system
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.cli import verify_profiles

if __name__ == "__main__":
    verify_profiles()

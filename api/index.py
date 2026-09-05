"""Vercel Serverless Function Entry Point for RiskLens AI.
Imports the main FastAPI application for serverless invocation.
"""
import os
import sys

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Export app for Vercel serverless runtime
__all__ = ["app"]

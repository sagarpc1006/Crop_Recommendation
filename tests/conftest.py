"""pytest configuration — ensures the project root is on sys.path
so that `import backend.*` works regardless of how pytest is invoked.
"""
import sys
import os

# Add the project root (parent of this file) to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
E-Commerce Analytics Dashboard
Main Streamlit application for deployment
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main web app
from web_app import main

if __name__ == "__main__":
    main() 
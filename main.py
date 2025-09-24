#!/usr/bin/env python3
"""
� STUDENT LEARNING PLATFORM - Education Management System �

Main entry point for the Student Learning Platform.
This script starts the Flask application with proper logging and error handling.

Usage:
    python main.py

Requirements:
    - .env file with required environment variables
    - All dependencies installed via requirements.txt
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the Flask app
try:
    from backend.app import app, logger, log_startup, log_success, log_error, log_info, log_warning
    from pymongo import MongoClient
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()

    # Show startup banner
    log_startup()

    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        log_error(".env file not found! Please create a .env file with required variables.")
        log_info("Required variables: MONGO_URI, SECRET_KEY")
        sys.exit(1)

    log_success("Environment file found")

    # Check required environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        log_error("SECRET_KEY environment variable is not set. Please check your .env file.")
        sys.exit(1)

    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        log_error("MONGO_URI environment variable is not set. Please check your .env file.")
        sys.exit(1)

    # Test MongoDB connection
    try:
        client = MongoClient(MONGO_URI)
        db_name = os.getenv('DB_NAME', 'student_learning')
        db = client[db_name]
        # Test the connection
        client.admin.command('ping')
        log_success(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        log_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    # Create indexes for better performance
    try:
        users_collection = db.users
        users_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        log_success("Database indexes created successfully")
    except Exception as e:
        log_warning(f"Index creation warning: {e}")

    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    log_info(f"Starting Student Learning Platform server on {host}:{port}")
    log_info(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
    log_success("� Student Learning Platform is ready! Press Ctrl+C to stop.")
    print(f"\n{'='*60}")
    print(f"🌐 ACCESS YOUR STUDENT LEARNING PLATFORM:")
    print(f"   Local:   http://localhost:{port}")
    print(f"   Network: http://127.0.0.1:{port}")
    print(f"   External: http://192.168.1.7:{port}")
    print(f"{'='*60}")
    print(f"💡 TIP: Click the links above or copy them to your browser!")
    print(f"{'='*60}\n")

    # Auto-open browser only once (check if already opened)
    browser_opened_file = current_dir / '.browser_opened'
    if not browser_opened_file.exists():
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')
            # Mark that browser was opened
            browser_opened_file.touch()

        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    else:
        log_info("Browser already opened previously - skipping auto-open")

    try:
        app.run(debug=debug_mode, host=host, port=port)
    except KeyboardInterrupt:
        log_info("Shutting down Student Learning Platform...")
        log_success("👋 Student Learning Platform stopped successfully!")
    except Exception as e:
        log_error(f"Student Learning Platform crashed: {e}")
        sys.exit(1)
#!/usr/bin/env python3

import os
import sys

# Set environment variables
os.environ['RENDER_DISK_PATH'] = './persistent_data'
os.environ['FLASK_APP'] = 'ppt_flask.py'
os.environ['FLASK_ENV'] = 'development'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ppt_flask import app
    print("✅ Flask app imported successfully")
    
    # Test if we can create the app
    with app.test_client() as client:
        print("✅ Test client created successfully")
    
    print("🚀 Starting Flask server...")
    app.run(host='0.0.0.0', port=5002, debug=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 
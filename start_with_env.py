#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables (override .env for local development)
env_vars = {
    'FLASK_ENV': 'deployment',
    'FLASK_DEBUG': 'true',
    'ALLOWED_ORIGINS': 'http://localhost:5173',
    'RENDER_DISK_PATH': './persistent_data',  # Use local path instead of /opt/render
}

for key, value in env_vars.items():
    os.environ[key] = value  # Always override for local development

# Print environment status
print("🔧 Environment Configuration:")
print(f"   FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"   FLASK_DEBUG: {os.getenv('FLASK_DEBUG')}")
print(f"   ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS')}")
print(f"   RENDER_DISK_PATH: {os.getenv('RENDER_DISK_PATH')}")
print(f"   OPENROUTER_API_KEY: {'✅ Set' if os.getenv('OPENROUTER_API_KEY') else '❌ Not set'}")
print(f"   R2_ACCOUNT_ID: {'✅ Set' if os.getenv('R2_ACCOUNT_ID') else '❌ Not set'}")
print(f"   R2_ACCESS_KEY_ID: {'✅ Set' if os.getenv('R2_ACCESS_KEY_ID') else '❌ Not set'}")
print(f"   R2_SECRET_ACCESS_KEY: {'✅ Set' if os.getenv('R2_SECRET_ACCESS_KEY') else '❌ Not set'}")
print(f"   R2_BUCKET_NAME: {'✅ Set' if os.getenv('R2_BUCKET_NAME') else '❌ Not set'}")
print(f"   R2_ENDPOINT_URL: {'✅ Set' if os.getenv('R2_ENDPOINT_URL') else '❌ Not set'}")
print()

# Create persistent data directory
persistent_data_path = os.getenv('RENDER_DISK_PATH', './persistent_data')
os.makedirs(persistent_data_path, exist_ok=True)
print(f"📁 Created persistent data directory: {persistent_data_path}")

# Import and start the Flask app
try:
    from ppt_flask import app
    print("✅ Flask app imported successfully")
    
    # Test S3 service
    from modules.s3_service import get_s3_service
s3_service = get_s3_service()
if s3_service.is_available():
        print("✅ S3 service is available")
    else:
        print("⚠️  S3 service is not available (this is okay for local development)")
    
    print("🚀 Starting Flask server...")
    print("🌐 Server will be available at: http://localhost:5002")
    print("📊 Health check: http://localhost:5002/health")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    app.run(host='0.0.0.0', port=5002, debug=True)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc() 
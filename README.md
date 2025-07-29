# AI Presentation Generator Service

This service provides AI-powered presentation generation for the CoXist AI platform.

## Features

- 🤖 AI-powered presentation content generation using OpenRouter API
- 📊 Professional PowerPoint creation with custom layouts
- 🌐 JSON API for web integration
- 📁 S3/R2 cloud storage integration
- 📤 Export to PowerPoint and PDF formats
- ✏️ Real-time slide editing and updates

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
RENDER_DISK_PATH=./persistent_data
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Start the Service

#### Option A: Using the startup script (recommended)

```bash
./start_server.sh
```

#### Option B: Manual start

```bash
export RENDER_DISK_PATH=./persistent_data
export FLASK_APP=ppt_flask.py
export FLASK_ENV=development
python test_server.py
```

### 4. Verify the Service

The service will be available at:

- **Main API**: http://localhost:5002
- **Health Check**: http://localhost:5002/health

## API Endpoints

### Create Presentation

```bash
POST /create_presentation
Content-Type: application/json

{
  "topic": "Machine Learning Basics",
  "slides": 5
}
```

### Get Presentation JSON

```bash
GET /get_presentation_json/{presentation_id}
```

### Export Presentation

```bash
POST /export_ppt
Content-Type: application/json

{
  "presentationId": "presentation_id",
  "format": "pptx"
}
```

### Update Slide

```bash
PUT /update_slide
Content-Type: application/json

{
  "presentation_id": "presentation_id",
  "slide_index": 0,
  "content": "Updated slide content"
}
```

## Integration with Frontend

The frontend (coxistai-fullstack) connects to this service via the `VITE_PPT_API_URL` environment variable:

```env
VITE_PPT_API_URL=http://localhost:5002
```

## Troubleshooting

### Service Won't Start

1. Check if port 5002 is available: `netstat -tlnp | grep 5002`
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Check environment variables are set correctly
4. Verify the persistent data directory is writable

### API Connection Issues

1. Verify the service is running: `curl http://localhost:5002/health`
2. Check CORS settings in the frontend
3. Ensure the `VITE_PPT_API_URL` is set correctly

### AI Generation Fails

1. Verify your OpenRouter API key is valid
2. Check the API key has sufficient credits
3. Review the service logs for detailed error messages

## Development

### Project Structure

```
coxistai-ppt-maker/
├── ppt_flask.py          # Main Flask application
├── modules/
│   ├── pptfinal.py       # AI content generation
│   └── s3_service.py     # Cloud storage integration
├── persistent_data/       # Local storage for presentations
├── requirements.txt       # Python dependencies
└── start_server.sh       # Startup script
```

### Adding New Features

1. Add new endpoints in `ppt_flask.py`
2. Implement business logic in `modules/`
3. Update API documentation
4. Test with the frontend integration

## Production Deployment

For production deployment on Render:

1. The service is configured to run on Render with the `render.yaml` file
2. Set environment variables in the Render dashboard
3. The service will automatically scale based on demand
4. Persistent storage is handled by Render's disk service

## Support

For issues or questions:

1. Check the service logs: `tail -f ppt_service.log`
2. Verify the health endpoint: `curl http://localhost:5002/health`
3. Test individual API endpoints
4. Review the frontend console for error messages

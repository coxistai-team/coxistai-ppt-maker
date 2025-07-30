# AI Presentation Generator Service

This service provides AI-powered presentation generation for the CoXist AI platform.

## Features

- 🤖 AI-powered presentation content generation using OpenRouter API
- 📊 Professional PowerPoint creation with enhanced designs and layouts
- 🎨 Multiple color themes and professional typography
- 🖼️ Unsplash image integration for visual enhancement
- 🌐 JSON API for web integration
- 📁 Cloudflare R2 cloud storage integration
- 📤 Export to PowerPoint and PDF formats
- ✏️ Real-time slide editing and updates
- 🎯 Thank you slide with professional conclusion
- ☁️ Automatic file storage and retrieval from R2

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
UNSPLASH_API_KEY=your_unsplash_api_key_here
R2_ACCOUNT_ID=your_r2_account_id_here
R2_ACCESS_KEY_ID=your_r2_access_key_id_here
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key_here
R2_BUCKET_NAME=your_r2_bucket_name_here
R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
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

### Get File from R2

```bash
GET /get_file/{presentation_id}/{filename}
```

## Enhanced Features

### Professional Design

- **Color Themes**: Multiple professional color schemes (Blue, Dark, Purple)
- **Typography**: Professional fonts (Calibri, Segoe UI, Georgia)
- **Layouts**: Enhanced slide layouts with proper spacing and alignment
- **Visual Elements**: Background shapes, accent lines, and professional styling

### Image Integration

- **Unsplash API**: Automatic image fetching based on presentation topic
- **Image Fitting**: Smart image resizing and cropping for optimal slide placement
- **Fallback System**: Graceful handling when images are unavailable
- **Quality Optimization**: High-quality image processing with proper compression

### Enhanced Slides

- **Title Slide**: Professional introduction with topic and date
- **Content Slides**: Well-structured content with bullet points and images
- **Thank You Slide**: Professional conclusion slide with Q&A section
- **Responsive Design**: Optimized for different screen sizes and formats

### Cloudflare R2 Integration

- **Automatic Upload**: PowerPoint files and images automatically uploaded to R2
- **File Retrieval**: Direct access to files stored in R2 bucket
- **Metadata Storage**: Presentation data and JSON structures stored in R2
- **Fallback System**: Local storage when R2 is unavailable
- **Secure Access**: Proper authentication and access control

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

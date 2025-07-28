# Docker Deployment on Render

## Quick Deploy

1. **Push to GitHub** (if not already done)
2. **Connect to Render**:
   - Go to https://render.com
   - Create new "Web Service"
   - Connect your GitHub repo
   - Select `coxistai-ppt-maker` directory

## Environment Variables

Set these in Render dashboard:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:5173

# AI Content Generation
OPENROUTER_API_KEY=your_openrouter_api_key

# Cloudflare R2 Configuration
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=coxist-files
R2_ENDPOINT_URL=https://0d355632f6abe6c1e9312175a17a04bf.r2.cloudflarestorage.com

# Storage Configuration
RENDER_DISK_PATH=/opt/render/project/src/persistent_data
```

## Render Settings

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python ppt_flask.py`
- **Port**: `5002`

## Update Frontend

After deployment, update your frontend environment:

```env
VITE_PPT_API_URL=https://your-render-service.onrender.com
```

## Health Check

Test the deployment:

```bash
curl https://your-render-service.onrender.com/health
```

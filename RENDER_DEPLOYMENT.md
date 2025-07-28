# Deploying AI Presentation Service on Render

## 🚀 Quick Deployment Guide

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**

   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Ensure these files are in your repository:**
   - `render.yaml` - Render configuration
   - `requirements.txt` - Python dependencies
   - `gunicorn.conf.py` - Gunicorn configuration
   - `ppt_flask.py` - Main application
   - `modules/` - All module files

### Step 2: Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" → "Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository with your AI presentation service**
5. **Render will automatically detect the `render.yaml` file**

### Step 3: Configure Environment Variables

After the initial deployment, go to your service settings and add these environment variables:

#### Required Variables:

- `OPENROUTER_API_KEY` - Your OpenRouter API key for AI content generation

#### Optional Variables:

- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins (default: your frontend domain)
- `AWS_ACCESS_KEY_ID` - For S3 storage (optional)
- `AWS_SECRET_ACCESS_KEY` - For S3 storage (optional)
- `AWS_REGION` - S3 region (default: us-east-1)
- `S3_BUCKET_NAME` - S3 bucket name (optional)

### Step 4: Update Frontend Configuration

Update your frontend environment variables:

```env
# In your frontend .env file
VITE_PPT_API_URL=https://your-service-name.onrender.com
```

## 📋 Deployment Checklist

### ✅ Pre-Deployment

- [ ] Code is pushed to GitHub
- [ ] `render.yaml` is configured
- [ ] `requirements.txt` includes all dependencies
- [ ] `gunicorn.conf.py` is present
- [ ] All modules are included

### ✅ Post-Deployment

- [ ] Service is running (check logs)
- [ ] Health check endpoint responds
- [ ] Environment variables are set
- [ ] Frontend is configured with new API URL
- [ ] Test basic functionality

## 🔧 Configuration Details

### Render Service Configuration

The `render.yaml` file configures:

- **Service Type**: Web service
- **Environment**: Python 3.11
- **Plan**: Starter (free tier)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --config gunicorn.conf.py ppt_flask:app`
- **Persistent Disk**: 1GB for storing presentations
- **Environment Variables**: Configured for security

### Gunicorn Configuration

The `gunicorn.conf.py` optimizes for:

- **Performance**: Multiple workers based on CPU cores
- **Reliability**: Request limits and timeouts
- **Logging**: Structured access and error logs
- **Security**: Request size limits

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
curl https://your-service-name.onrender.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "s3_available": true,
  "openrouter_configured": true
}
```

### 2. Test Presentation Creation

```bash
curl -X POST https://your-service-name.onrender.com/create_presentation \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Presentation", "slides": 3}'
```

### 3. Test Slide Operations

```bash
# Copy slide
curl -X POST https://your-service-name.onrender.com/slide_operations \
  -H "Content-Type: application/json" \
  -d '{"operation": "copy", "presentation_id": "test", "slide_index": 0}'

# Delete slide
curl -X POST https://your-service-name.onrender.com/slide_operations \
  -H "Content-Type: application/json" \
  -d '{"operation": "delete", "presentation_id": "test", "slide_index": 0}'
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**

   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **Service Won't Start**

   - Verify `gunicorn.conf.py` is correct
   - Check start command in `render.yaml`
   - Review service logs

3. **Environment Variables Not Working**

   - Ensure variables are set in Render dashboard
   - Check variable names match code
   - Restart service after adding variables

4. **API Calls Fail**
   - Verify CORS configuration
   - Check `ALLOWED_ORIGINS` includes your frontend domain
   - Test with curl to isolate frontend/backend issues

### Checking Logs

1. **In Render Dashboard:**

   - Go to your service
   - Click "Logs" tab
   - Check for errors or warnings

2. **Common Log Messages:**
   ```
   INFO: Starting Enhanced AI Presentation Generator API
   INFO: S3 Status: Available/Not Available
   INFO: OpenRouter configured: True/False
   ```

## 📊 Monitoring

### Health Check Endpoint

- **URL**: `https://your-service.onrender.com/health`
- **Frequency**: Check every 5 minutes
- **Expected**: 200 OK with status "healthy"

### Key Metrics to Monitor

- Response time < 5 seconds
- Error rate < 1%
- Uptime > 99.9%
- Memory usage < 80%

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to repository
2. **CORS**: Configure `ALLOWED_ORIGINS` properly
3. **Rate Limiting**: Already configured (30 requests/minute)
4. **Input Validation**: All endpoints validate input
5. **HTTPS**: Render provides SSL automatically

## 🚀 Scaling

### Free Tier Limits

- 750 hours/month
- 512MB RAM
- 0.1 CPU
- 1GB disk

### Upgrading

- **Starter Plan**: $7/month for more resources
- **Standard Plan**: $25/month for production workloads
- **Pro Plan**: $50/month for high-traffic applications

## 📞 Support

If you encounter issues:

1. **Check Render Documentation**: https://render.com/docs
2. **Review Service Logs**: In Render dashboard
3. **Test Locally**: Run `python ppt_flask.py` to debug
4. **Verify Configuration**: Double-check `render.yaml` and environment variables

---

**Deployment Status**: ✅ Ready for production  
**Last Updated**: 2024  
**Maintainer**: Your Team

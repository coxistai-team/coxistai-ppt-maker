# Frontend Configuration for Render Deployment

## 🔧 Update Frontend Environment Variables

After deploying your AI Presentation service to Render, update your frontend configuration:

### 1. Update Environment Variables

In your frontend project (`coxistai-fullstack/client/`), update the environment variables:

```env
# .env file in your frontend
VITE_PPT_API_URL=https://your-service-name.onrender.com
```

Replace `your-service-name` with your actual Render service name.

### 2. Update CORS Configuration

In your Render service dashboard, set the `ALLOWED_ORIGINS` environment variable:

```
https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

### 3. Test the Integration

After updating the environment variables, test the integration:

1. **Start your frontend development server:**

   ```bash
   cd coxistai-fullstack/client
   npm run dev
   ```

2. **Navigate to the AI Presentations page**

3. **Test the features:**
   - Generate a new presentation
   - Copy slides
   - Delete slides
   - Export presentations

## 🧪 Testing Checklist

### ✅ Basic Functionality

- [ ] Health check endpoint responds
- [ ] Presentation generation works
- [ ] Slide operations (copy/delete) work
- [ ] Export functionality works

### ✅ UI/UX

- [ ] Dark theme is consistent
- [ ] No white components visible
- [ ] Loading states work properly
- [ ] Error messages are clear

### ✅ Integration

- [ ] Frontend connects to Render service
- [ ] CORS is properly configured
- [ ] Environment variables are set correctly

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**

   - Check `ALLOWED_ORIGINS` in Render dashboard
   - Ensure your frontend domain is included
   - Restart the Render service after changing CORS

2. **API Connection Failed**

   - Verify `VITE_PPT_API_URL` is correct
   - Check if Render service is running
   - Test with curl: `curl https://your-service.onrender.com/health`

3. **Environment Variables Not Working**

   - Restart your frontend development server
   - Check browser console for errors
   - Verify variable names match exactly

4. **Service Not Responding**
   - Check Render service logs
   - Verify service is not suspended (free tier)
   - Check if environment variables are set

### Debug Commands

```bash
# Test Render service health
curl https://your-service-name.onrender.com/health

# Test presentation creation
curl -X POST https://your-service-name.onrender.com/create_presentation \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test", "slides": 3}'

# Check frontend environment
echo $VITE_PPT_API_URL
```

## 📊 Monitoring

### Frontend Monitoring

- Check browser console for errors
- Monitor network requests in DevTools
- Test on different browsers

### Backend Monitoring

- Monitor Render service logs
- Check service uptime in Render dashboard
- Monitor API response times

## 🚀 Production Deployment

### Frontend Deployment

1. **Build for production:**

   ```bash
   npm run build
   ```

2. **Deploy to your hosting platform** (Vercel, Netlify, etc.)

3. **Update production environment variables**

### Environment Variables for Production

```env
# Production .env
VITE_PPT_API_URL=https://your-service-name.onrender.com
VITE_API_URL=https://your-backend-api.com
```

## 🔒 Security Notes

1. **API Keys**: Never expose API keys in frontend code
2. **CORS**: Configure properly for production domains
3. **HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Monitor API usage

## 📞 Support

If you encounter issues:

1. **Check Render service logs**
2. **Test API endpoints directly**
3. **Verify environment variables**
4. **Check CORS configuration**

---

**Status**: ✅ Ready for production deployment  
**Last Updated**: 2024

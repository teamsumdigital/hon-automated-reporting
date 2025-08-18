# 🚀 Render Deployment Steps - HON Backend

## **Manual Steps for Render Dashboard**

### **1. Create Web Service**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository: `teamsumdigital/hon-automated-reporting`

### **2. Configure Service**
- **Name**: `hon-automated-reporting-api`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **3. Environment Variables**
Copy these from `.env.production.example` and add your actual values:

**Required for basic functionality:**
```
ENVIRONMENT=production
DEBUG_MODE=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
```

**For Meta Ads (if needed):**
```
META_ACCESS_TOKEN=your_token
META_ACCOUNT_ID=your_account_id
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
```

**For Google Ads (if needed):**
```
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CUSTOMER_ID=1234567890
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_secret
GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token
```

**For TikTok Ads (if needed):**
```
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_APP_ID=your_app_id
TIKTOK_SECRET=your_secret
```

### **4. Deploy**
1. Click **"Create Web Service"**
2. Wait for build to complete (~2-3 minutes)
3. Note your Render URL: `https://your-service-name.onrender.com`

### **5. Test Deployment**
```bash
# Health check
curl https://your-service-name.onrender.com/health

# Should return:
{
  "status": "healthy",
  "environment": "production",
  "debug_mode": false
}
```

### **6. Update Netlify**
1. Copy your Render URL
2. Go to Netlify site settings → Environment variables
3. Add: `VITE_API_BASE_URL=https://your-service-name.onrender.com`
4. Redeploy Netlify site

### **7. Update Backend CORS**
1. In your code, update `main.py` line 30:
```python
# Add production Netlify URL after deployment:
"https://your-netlify-site.netlify.app",
```
2. Redeploy Render service

## **Expected Results**
- ✅ Backend health check responds
- ✅ Frontend connects to backend
- ✅ Authentication works
- ✅ Dashboard loads data

## **Troubleshooting**
- Check Render logs if build fails
- Verify environment variables are set
- Test health endpoint first
- Check CORS configuration if frontend can't connect
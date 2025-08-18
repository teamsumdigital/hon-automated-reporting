# 🚀 HON Automated Reporting - Deployment Guide

## 🌐 **Netlify Frontend Deployment**

### **Prerequisites**
- GitHub account with access to the repository
- Netlify account (free tier is sufficient)

### **Step 1: Netlify Setup**

1. **Connect Repository**
   - Go to [Netlify Dashboard](https://app.netlify.com/)
   - Click "New site from Git" 
   - Connect to GitHub and select `teamsumdigital/hon-automated-reporting`
   - Set build settings:
     - **Base directory**: `frontend`
     - **Build command**: `npm run build`
     - **Publish directory**: `frontend/dist`

2. **Environment Variables**
   ```
   VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
   ```

3. **Deploy Settings**
   - **Node version**: 18
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`

### **Step 2: Domain & Security**

1. **Custom Domain** (Optional)
   - Add custom domain in Netlify settings
   - Configure DNS records as instructed

2. **Security Headers** 
   - Already configured in `netlify.toml`
   - Includes SEO blocking and security headers

3. **HTTPS**
   - Automatically enabled by Netlify
   - Free SSL certificates included

---

## ⚙️ **Render Backend Deployment**

### **Prerequisites**
- GitHub account with repository access
- Render account (free tier available)

### **Step 1: Render Setup**

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect GitHub repository: `teamsumdigital/hon-automated-reporting`
   - Set configuration:
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Step 2: Environment Variables**

Set these in Render dashboard under "Environment":

```env
# Meta Ads API
META_ACCESS_TOKEN=your_meta_access_token
META_ACCOUNT_ID=your_meta_account_id
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret

# Google Ads API  
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CUSTOMER_ID=1234567890
GOOGLE_OAUTH_CLIENT_ID=your_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token

# TikTok Ads API
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
TIKTOK_APP_ID=your_tiktok_app_id
TIKTOK_SECRET=your_tiktok_secret

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Application Settings
DEBUG_MODE=false
ENVIRONMENT=production
```

### **Step 3: Deploy & Test**

1. **Initial Deploy**
   - Click "Create Web Service"
   - Wait for build to complete (~2-3 minutes)
   - Check logs for any errors

2. **Health Check**
   ```bash
   curl https://your-render-app.onrender.com/health
   ```

3. **Update Frontend**
   - Copy your Render URL
   - Update Netlify environment variable `VITE_API_BASE_URL`
   - Redeploy frontend

---

## 🔗 **Connect Frontend & Backend**

### **Update Netlify Environment**

1. Go to Netlify Site Settings → Environment Variables
2. Add/Update:
   ```
   VITE_API_BASE_URL=https://your-render-backend.onrender.com
   ```
3. Redeploy site

### **Test Full Stack**

1. **Frontend**: Visit your Netlify URL
2. **Authentication**: Enter password: `HN$7kX9#mQ2vL8pR@2024`
3. **API Connection**: Check if data loads correctly
4. **Sync Test**: Try manual data sync

---

## 🔐 **Security Checklist**

### **Frontend Security**
- ✅ Password protection enabled
- ✅ SEO blocking (`noindex` meta tags)
- ✅ Security headers in `netlify.toml`
- ✅ HTTPS enforced by Netlify

### **Backend Security**
- ✅ Environment variables for secrets
- ✅ CORS configured for frontend domain
- ✅ API rate limiting (if needed)
- ✅ HTTPS enforced by Render

### **Database Security**
- ✅ Supabase RLS (Row Level Security)
- ✅ Service key access only
- ✅ No public database access

---

## 🚨 **Post-Deployment Tasks**

### **1. Update Password Storage**
Move password to environment variable for better security:

**Frontend** (`AuthGate.tsx`):
```typescript
const correctPassword = import.meta.env.VITE_AUTH_PASSWORD || 'fallback_password';
```

**Netlify Environment**:
```
VITE_AUTH_PASSWORD=HN$7kX9#mQ2vL8pR@2024
```

### **2. Configure CORS**
Update backend CORS for production domain:

**Backend** (`main.py`):
```python
origins = [
    "https://your-netlify-site.netlify.app",  # Add your Netlify URL
    "http://localhost:3007",  # Keep for development
]
```

### **3. Test All Features**
- [ ] Authentication works
- [ ] All three tabs load (Meta, Google, TikTok)
- [ ] Data sync functionality
- [ ] Category filtering
- [ ] Month navigation
- [ ] Export functionality

### **4. Monitor & Maintain**
- Check Render logs for errors
- Monitor Netlify build logs
- Set up uptime monitoring
- Regular security updates

---

## 📊 **Expected URLs**

After deployment, you'll have:

- **Frontend**: `https://your-site-name.netlify.app`
- **Backend**: `https://your-service-name.onrender.com`
- **Health Check**: `https://your-service-name.onrender.com/health`

---

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   - Check Node.js version (should be 18+)
   - Verify build command and directory paths
   - Check for missing dependencies

2. **API Connection Issues**
   - Verify `VITE_API_BASE_URL` in Netlify
   - Check CORS configuration in backend
   - Ensure backend is deployed and healthy

3. **Authentication Issues**
   - Verify password is correct
   - Check localStorage is enabled
   - Clear browser cache if needed

4. **Data Loading Issues**
   - Check backend environment variables
   - Verify Supabase connection
   - Check API logs in Render dashboard

### **Getting Help**
- Check deployment logs in Netlify/Render dashboards
- Test API endpoints directly with curl
- Verify environment variables are set correctly

---

**🎉 Ready to deploy! Follow the steps above to get HON Automated Reporting live in production.**
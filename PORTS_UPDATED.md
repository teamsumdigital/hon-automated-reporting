# ✅ Ports Updated - HON Automated Reporting

## 🔄 **Port Configuration Updated**

The system has been updated to use dedicated ports:

### **🚀 Server URLs**
- **Backend API**: http://localhost:8007 ✅
- **Frontend Dashboard**: http://localhost:3007 ✅

### **📝 What Was Updated**
1. **Backend Configuration**: 
   - `main.py` now defaults to port 8007
   - Environment variable `BACKEND_URL=http://localhost:8007`

2. **Frontend Configuration**:
   - `package.json` dev script uses port 3007
   - `vite.config.ts` server port set to 3007
   - Proxy configuration points to backend port 8007
   - API client defaults to port 8007

3. **n8n Workflow**:
   - Webhook URLs updated to port 8007
   - All HTTP request nodes point to correct backend port

4. **Documentation**:
   - README updated with new ports
   - All references to ports corrected

### **✅ Current Status**
- **Backend**: Running on http://localhost:8007 ✅
- **Frontend**: Running on http://localhost:3007 ✅  
- **API Health**: Confirmed working ✅
- **Dashboard Data**: Previously synced data available ✅

### **🌐 Access Your Dashboard**
**Visit: http://localhost:3007**

Your automated Meta Ads reporting dashboard is now available on the dedicated ports!

### **📊 Available Data**
The system has your previously synced campaign data:
- **Total Spend**: $71,267.34
- **Total Revenue**: $413,936.86
- **Categories**: Bath Mats, Play Furniture, Play Mats, Standing Mats, Tumbling Mats
- **Performance Metrics**: ROAS, CPA, CPC all calculated

### **🔄 Next Steps**
1. Visit http://localhost:3007 to access the dashboard
2. Click "Sync Data" to pull fresh campaign data
3. Explore the interactive pivot table and category filters
4. Use the dashboard for your weekly reporting meetings

---

**Standard Ports for HON Automated Reporting:**
- **Backend**: 8007
- **Frontend**: 3007

These ports are now consistent across all configuration files and documentation.
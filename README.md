# HON Automated Reporting System

A complete automated reporting solution for House of Noa's multi-platform advertising campaigns with enhanced ad name parsing, weekly segmentation, real ad ID verification, and comprehensive platform support.

## 🎯 Features

### Multi-Platform Support
- **Meta Ads Integration**: Enhanced parsing with dual account support and real ad ID verification
- **Google Ads Integration**: Native Google Ads API integration with proper conversion tracking
- **TikTok Ads Integration**: Complete TikTok Marketing API integration
- **OpenAI Integration**: AI-powered data analysis and insights
- **Excel-Style Tabs**: Switch between platform dashboards with bottom tab navigation
- **Unified Categorization**: Same product categorization system works across all platforms

### Data & Analytics  
- **Ad-Level Data**: 14-day periods with weekly segmentation and real Meta ad IDs
- **Enhanced Parsing**: 100% accurate ad name parsing with launch dates and product extraction
- **Smart Filtering**: Removes ads with $0 spend and 0 purchases (keeps interesting edge cases)
- **Dual Storage**: Original platform ad names + cleaned parsed versions
- **Real-time Dashboards**: React frontend with comprehensive filtering and analytics
- **Campaign Categorization**: Advanced categorization by product lines, colors, formats, and optimization types

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Meta Ads API Integration**: Dual account support with enhanced parsing and real ad ID verification
- **Supabase Database**: Ad-level data storage with weekly segmentation and dual ad name fields
- **Advanced Parsing**: 100% accurate extraction of launch dates, products, colors, formats, and optimization types
- **Smart Filtering**: Automatic removal of low-value ads ($0 spend + 0 purchases)
- **Rate Limiting**: Production-ready API calls with proper retry logic

### Frontend (React + Vite)
- **Modern Dashboard**: Clean interface with KPI cards and pivot tables
- **Category Filtering**: Filter by product categories
- **Month-by-Month View**: Expandable monthly breakdowns
- **Responsive Design**: Works on desktop and mobile

### Automation (n8n)
- **Daily Workflow**: Scheduled 5am data pulls
- **Link Clicks Extraction**: Proper API field handling
- **Database Integration**: Direct Supabase upserts

## 📊 Key Metrics Fixed

### Before Fix (Incorrect)
- **January 2024**: $4.2M spend, 233K clicks, $18.02 CPC ❌
- **Data Source**: Total clicks (all ad engagements)

### After Fix (Correct)
- **January 2024**: $219K spend, 165K clicks, $1.33 CPC ✅
- **Data Source**: Link clicks only (website clicks)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13+
- Meta Ads API credentials (dual account support)
- Google Ads API credentials
- TikTok Marketing API credentials
- OpenAI API key
- Supabase account
- n8n instance (optional)

### Installation

1. **Clone repository**
```bash
git clone https://github.com/teamsumdigital/hon-automated-reporting.git
cd hon-automated-reporting
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your credentials:
# META_ACCESS_TOKEN=your_meta_token
# META_ACCOUNT_ID=your_primary_account_id
# META_ACCOUNT_ID_SECONDARY=your_secondary_account_id
# META_APP_ID=your_app_id
# META_APP_SECRET=your_app_secret
# SUPABASE_URL=your_supabase_url
# SUPABASE_SERVICE_KEY=your_service_key
# OPENAI_API_KEY=your_openai_key
# GOOGLE_ADS_DEVELOPER_TOKEN=your_google_token
# TIKTOK_ACCESS_TOKEN=your_tiktok_token
```

4. **Database Setup**
```bash
python setup_database.py
```

5. **Frontend Setup**
```bash
cd ../frontend
npm install
```

### Running the Application

1. **Start Backend** (Terminal 1)
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8007
```

2. **Start Frontend** (Terminal 2)
```bash
cd frontend
npm run dev
```

3. **Access Dashboard**
```
Frontend: http://localhost:3007
Backend API: http://localhost:8007
```

## 📁 Project Structure

```
hon-automated-reporting/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── core/          # Core utilities
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Dashboard pages
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   └── package.json       # Node dependencies
├── database/
│   └── schema.sql         # Database schema
├── scripts/
│   ├── resync_historic_data.py      # Full historical resync
│   ├── fix_august_2025.py          # August 2025 fix
│   └── clean_proper_resync.py      # Clean database resync
└── n8n-workflows/
    └── meta-ads-daily-pull.json    # n8n automation workflow
```

## 🔧 Key Scripts

### Historical Data Management
```bash
# Full clean resync (clears all data)
python clean_proper_resync.py

# Historical data resync (preserves existing data)
python resync_historic_data.py

# Fix specific month (example: August 2025)
python fix_august_2025.py
```

### API Testing
```bash
# Test Meta API connection
curl http://localhost:8007/api/reports/test-connection

# Get monthly data
curl http://localhost:8007/api/reports/monthly

# Health check
curl http://localhost:8007/health
```

## 🎯 Meta API Integration

### Critical Fix: Link Clicks Extraction

**Problem**: Original implementation used top-level `clicks` field (total ad clicks)
**Solution**: Extract `link_clicks` from `actions` array (website clicks only)

```python
# BEFORE (Incorrect)
clicks = insight.get('clicks', '0')  # Total clicks

# AFTER (Correct)
link_clicks = "0"
if 'actions' in insight and insight['actions']:
    for action in insight['actions']:
        if action.get('action_type') == 'link_click':
            link_clicks = action.get('value', '0')
            break
```

### API Fields Required
```python
'fields': [
    'campaign_id',
    'campaign_name', 
    'spend',
    'actions',           # Required for link_clicks
    'action_values',     # Required for purchase values
    'impressions',
    'clicks',
    'cpm', 'cpc', 'ctr'
]
```

## 📈 Campaign Categorization

Automatic categorization rules:
- **Play Mats**: `['play', 'mat']`
- **Standing Mats**: `['standing', 'desk']`
- **Bath Mats**: `['bath', 'mat']`
- **Tumbling Mats**: `['tumbling']`
- **Play Furniture**: `['play', 'furniture']`
- **Multi Category**: `['multi']`

## 🔄 Daily Automation (n8n)

### Workflow Schedule
- **Time**: 5:00 AM daily
- **Data**: Previous day's campaign performance
- **Processing**: Link clicks extraction + categorization
- **Storage**: Direct Supabase upsert

### Key n8n Nodes
1. **Cron Trigger**: Daily at 5 AM
2. **Meta API Call**: Fetch yesterday's data
3. **Data Processing**: Extract link_clicks from actions
4. **Categorization**: Apply product line rules
5. **Database Insert**: Upsert to Supabase

## 🚨 Important Notes

### Data Accuracy
- **Link Clicks**: Always extracted from `actions` array with `action_type: 'link_click'`
- **CPC Calculation**: `spend / link_clicks` (not total clicks)
- **Date Ranges**: Month-specific ranges to avoid duplicates

### Database Constraints
- **Unique Key**: `(campaign_id, reporting_starts, reporting_ends)`
- **Prevents Duplicates**: Upsert operations handle conflicts
- **Data Integrity**: Proper date range enforcement

## 📊 Expected Performance Metrics

### Realistic CPC Ranges
- **Jan 2024**: $1.33 CPC
- **Feb 2024**: $1.44 CPC
- **Aug 2025**: $1.43 CPC
- **Overall Range**: $1.30 - $2.20

### Data Volume
- **20 months** of historical data
- **~300 total campaigns** across all months
- **Daily updates** starting August 12, 2025

## 🔐 Environment Variables

```env
# Meta Ads API (Dual Account Support)
META_APP_ID=1459737788539040
META_APP_SECRET=30d048bf9f62385947e256245ca7d713
META_ACCOUNT_ID=12838773
META_ACCOUNT_ID_SECONDARY=728880056795187
META_ACCESS_TOKEN=your_long_lived_token

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=-gJOMMcQIcQBxKuaUd0FhA
GOOGLE_ADS_CUSTOMER_ID=9860652386
GOOGLE_ADS_LOGIN_CUSTOMER_ID=2301612041
GOOGLE_OAUTH_CLIENT_ID=1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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
GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token

# TikTok Marketing API
TIKTOK_APP_ID=7538619599563161616
TIKTOK_APP_SECRET=51c35c7f4f089c33d793f709abc88bba293f6c83
TIKTOK_ACCESS_TOKEN=a3d1496268b35f9ad9a6f0d9d4492ab35d4c0bea
TIKTOK_ADVERTISER_ID=6961828676572839938
TIKTOK_SANDBOX_MODE=false

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Supabase Database
SUPABASE_URL=https://pncdozcbrdmulkylazmd.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# n8n Integration
N8N_WEBHOOK_URL=your_n8n_webhook_url

# Application Settings
APP_ENV=development
DEBUG_MODE=true
LOG_LEVEL=INFO
FRONTEND_URL=http://localhost:3007
BACKEND_URL=http://localhost:8007
```

## 🚀 Google Ads API Setup

### Prerequisites
1. **Google Cloud Console Project**
   - Create or select a project at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Ads API
   - Set up OAuth2 credentials (Web application type)

2. **Google Ads Developer Access**
   - Apply for Google Ads API access at [Google Ads API Center](https://ads.google.com/home/tools/manager-accounts/)
   - This requires business verification and may take several days
   - You'll need a Google Ads Manager account

### Step-by-Step Setup

#### 1. Create OAuth2 Credentials
```bash
# In Google Cloud Console:
# 1. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
# 2. Application type: "Web application"
# 3. Add authorized redirect URI: http://localhost:8080/oauth2callback
# 4. Download the JSON file
```

#### 2. Get Refresh Token
```bash
# Use the Google Ads API authentication tool:
# https://developers.google.com/google-ads/api/docs/first-call/overview

# Or run this Python script:
python -c "
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'path/to/client_secrets.json',
    scopes=['https://www.googleapis.com/auth/adwords']
)
creds = flow.run_local_server(port=8080)
print('Refresh Token:', creds.refresh_token)
"
```

#### 3. Configure Environment Variables
```env
# Copy from Google Cloud Console OAuth2 credentials
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

# From Step 2 authentication
GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token

# From Google Ads account (10-digit number without dashes)
GOOGLE_ADS_CUSTOMER_ID=1234567890

# Developer token from Google Ads Manager account
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token

# Optional: Manager account ID for manager accounts
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_account_id
```

#### 4. Run Database Migration
```bash
# Create Google Ads tables in Supabase
python run_google_ads_migration.py

# Or run the SQL directly in Supabase dashboard
# File: database/migrations/add_google_campaign_data.sql
```

#### 5. Test Connection & Sync Data
```bash
# Test Google Ads API connection
curl http://localhost:8007/api/google-reports/test-connection

# Sync historical data (this may take several minutes)
python google_historical_resync.py
```

## 🐛 Troubleshooting

### Common Issues

1. **High CPC Values ($10+)**
   - **Cause**: Using total clicks instead of link_clicks
   - **Fix**: Verify link_clicks extraction from actions array

2. **Duplicate Data**
   - **Cause**: Overlapping date ranges in resync
   - **Fix**: Run `clean_proper_resync.py`

3. **Missing Link Clicks**
   - **Cause**: Meta API not returning actions data
   - **Fix**: Check API permissions and field requests

### API Connection Issues
```bash
# Test connection
python -c "from app.services.meta_api import MetaAdsService; print('✅ Connected' if MetaAdsService().test_connection() else '❌ Failed')"
```

## 📝 API Endpoints

### Reports
- `GET /api/reports/monthly` - Monthly breakdown data
- `GET /api/reports/campaigns` - Campaign-level data
- `GET /api/reports/dashboard` - Dashboard summary
- `POST /api/reports/sync` - Manual data sync

### Health & Testing
- `GET /health` - Application health check
- `GET /api/reports/test-connection` - Meta API connection test

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is proprietary to Sum Digital Inc. and House of Noa.

## 🔗 Links

- **Repository**: https://github.com/teamsumdigital/hon-automated-reporting
- **Meta Ads API**: https://developers.facebook.com/docs/marketing-api/
- **Supabase**: https://supabase.com/docs
- **n8n**: https://docs.n8n.io/

---

**Built with ❤️ by Sum Digital for House of Noa**
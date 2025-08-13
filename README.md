# HON Automated Reporting

An automated Meta Ads reporting system that replaces manual Excel workflows with a real-time web dashboard featuring pivot tables, category filtering, and scheduled data synchronization.

## 🌟 Features

- **Automated Data Collection**: n8n workflows pull Meta Ads data daily
- **Smart Categorization**: Rule-based campaign categorization with manual overrides
- **Interactive Dashboard**: React-based UI recreating Excel pivot table functionality
- **Category Filtering**: Multi-select category slicer matching Excel functionality
- **Month-to-Date Calculations**: Automatic date range calculations for weekly reports
- **Real-time Sync**: Manual and scheduled data synchronization
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   n8n Workflow  │───▶│  FastAPI Backend │───▶│ Supabase Database│
│  (Scheduled)     │    │   (Python)       │    │  (PostgreSQL)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ React Frontend   │
                       │   (Dashboard)    │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Meta Ads API   │
                       │   (Data Source)  │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Supabase** account (for database)
- **Meta Ads API** access token
- **n8n** instance (for automation)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hon-automated-reporting

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your credentials:

```env
# Meta Ads API (REQUIRED)
META_APP_ID=1459737788539040
META_APP_SECRET=30d048bf9f62385947e256245ca7d713
META_ACCOUNT_ID=12838773
META_ACCESS_TOKEN=your_long_lived_token_here

# Database (REQUIRED)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Application Settings
APP_ENV=development
DEBUG_MODE=true
```

### 3. Database Setup

1. **Create Supabase Project**: Visit [supabase.com](https://supabase.com) and create a new project
2. **Run Database Schema**: Execute the SQL in `database/schema.sql` in your Supabase SQL editor
3. **Verify Tables**: Ensure these tables are created:
   - `campaign_data`
   - `category_rules`
   - `category_overrides`
   - `monthly_reports`

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

Backend will run on `http://localhost:8007`

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will run on `http://localhost:3007`

### 6. Test the Setup

1. **Visit Dashboard**: Navigate to `http://localhost:3007`
2. **Test Meta Connection**: Click "Sync Data" to test Meta Ads API
3. **Check Database**: Verify data appears in Supabase tables

## 📊 Dashboard Features

### Pivot Table
Recreates your Excel pivot table with columns:
- Month
- Spend (USD)
- Link Clicks
- Purchases  
- Revenue (USD)
- CPA (Cost Per Acquisition)
- ROAS (Return on Ad Spend)
- CPC (Cost Per Click)

### Category Filter
Multi-select dropdown supporting:
- Individual category selection
- Select all / Clear all
- Real-time filtering
- Visual chips for selected categories

### Metrics Cards
Key performance indicators:
- Total Spend
- Total Revenue
- ROAS
- CPA
- Link Clicks
- Impressions

### Category Breakdown
Performance by category showing spend, purchases, revenue, and efficiency metrics.

## 🤖 n8n Automation

### Workflow: Daily Meta Ads Pull

**Schedule**: Weekdays at 9:00 AM

**Process**:
1. Calculate month-to-date date range
2. Trigger backend sync via webhook
3. Send Slack notifications (optional)
4. Generate performance summary

### Setup Instructions

1. **Import Workflow**: Import `n8n-workflows/meta-ads-daily-pull.json` into your n8n instance
2. **Configure URLs**: Update HTTP request nodes to point to your backend
3. **Set Credentials**: Configure Slack integration (optional)
4. **Activate**: Enable the workflow in n8n

### Webhook Endpoints

The workflow calls these endpoints:

- **Sync Trigger**: `POST /api/webhook/n8n-trigger`
- **Get Summary**: `GET /api/reports/month-to-date`

## 🗂️ Campaign Categorization

### Automatic Rules

Categories are assigned based on campaign name patterns:

| Pattern | Category |
|---------|----------|
| %Bath% | Bath Mats |
| %Play Furniture% | Play Furniture |
| %Play%Mat% | Play Mats |
| %Standing% | Standing Mats |
| %Tumbling% | Tumbling Mats |
| %Creative Testing% | Multi Category |
| %High Chair% | High Chair Mats |

### Manual Overrides

- Override automatic categorization for specific campaigns
- Managed through the backend API
- Persistent across data syncs

### Adding New Rules

Use the backend API to add categorization rules:

```bash
curl -X POST http://localhost:8000/api/reports/category-rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "New Category Rule",
    "pattern": "keyword",
    "category": "New Category",
    "priority": 1
  }'
```

## 📅 Date Range Logic

### Month-to-Date for Weekly Reports

For weekly meetings, the system calculates:
- **Start Date**: First day of current month
- **End Date**: Day before meeting date

**Example**: For an August 18 meeting:
- Start: August 1
- End: August 17

This provides month-to-date performance up to the day before the meeting.

## 🛠️ API Reference

### Dashboard Data
```http
GET /api/reports/dashboard?categories=Bath%20Mats,Play%20Mats&start_date=2024-08-01&end_date=2024-08-17
```

### Sync Meta Data
```http
POST /api/reports/sync
Content-Type: application/json

{
  "target_date": "2024-08-18"
}
```

### Get Categories
```http
GET /api/reports/categories
```

### Health Check
```http
GET /health
```

## 🚀 Deployment

### Backend Deployment

**Docker**:
```bash
cd backend
docker build -t hon-reporting-backend .
docker run -p 8000:8000 --env-file .env hon-reporting-backend
```

**Traditional**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

**Build for Production**:
```bash
cd frontend
npm run build
```

**Deploy to Netlify/Vercel**:
- Upload `dist/` folder to your hosting provider
- Configure environment variables
- Set up redirects for SPA routing

### Environment Variables for Production

Update `.env` with production values:
```env
APP_ENV=production
DEBUG_MODE=false
SUPABASE_URL=https://your-project.supabase.co
META_ACCESS_TOKEN=your_production_token
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

## 🔧 Troubleshooting

### Common Issues

**"Meta API Connection Failed"**
- Verify `META_ACCESS_TOKEN` is valid and not expired
- Check Meta App permissions include ads_read
- Ensure account ID is correct

**"Database Connection Error"**
- Verify Supabase URL and service key
- Check database schema is created
- Ensure service key has necessary permissions

**"No Data in Dashboard"**
- Run manual sync: click "Sync Data" button
- Check backend logs for API errors
- Verify date range includes campaign activity

**"Categories Not Loading"**
- Check database schema includes `category_rules` table
- Verify default rules were inserted
- Check backend API connectivity

### Debug Mode

Enable debug logging:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

Check logs:
- **Backend**: `backend/logs/hon_reporting.log`
- **Frontend**: Browser developer console
- **n8n**: n8n execution history

### Database Queries

Useful SQL queries for debugging:

```sql
-- Check recent campaign data
SELECT * FROM campaign_data 
ORDER BY created_at DESC 
LIMIT 10;

-- Category distribution
SELECT category, COUNT(*) as count 
FROM campaign_data 
GROUP BY category;

-- Monthly spend totals
SELECT 
  DATE_TRUNC('month', reporting_starts) as month,
  SUM(amount_spent_usd) as total_spend
FROM campaign_data 
GROUP BY month 
ORDER BY month DESC;
```

## 📈 Performance

### Optimization Tips

- **Database Indexing**: Indexes are created on frequently queried fields
- **Query Caching**: Frontend uses React Query for intelligent caching
- **API Rate Limits**: Backend respects Meta API rate limits
- **Pagination**: Large datasets are paginated automatically

### Monitoring

- **Backend Health**: `GET /health`
- **Meta API Status**: `GET /api/reports/test-connection`
- **Database Performance**: Monitor query execution times in Supabase

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit with descriptive messages
5. Push and create pull request

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use Prettier and ESLint configurations
- **Commits**: Use conventional commit format

## 📄 License

This project is proprietary software for HON internal use.

## 📞 Support

For questions or issues:
1. Check this README and troubleshooting section
2. Review backend logs and frontend console
3. Contact the development team

---

**Last Updated**: August 2024  
**Version**: 1.0.0
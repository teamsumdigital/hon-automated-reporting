# n8n Workflows for HON Automated Reporting

This directory contains n8n workflow configurations for automating Meta Ads data collection and reporting.

## Workflows

### 1. meta-ads-daily-pull.json

**Purpose**: Automatically pulls Meta Ads campaign data daily and triggers backend processing.

**Schedule**: Weekdays at 9:00 AM (Monday-Friday)

**Flow**:
1. **Schedule Trigger** → Runs at 9 AM on weekdays
2. **Calculate Date Range** → Determines month-to-date date range
3. **Trigger Backend Sync** → Calls webhook to start data sync
4. **Check Response** → Validates sync was accepted
5. **Success Path** → Sends success notification + MTD summary
6. **Error Path** → Handles failures and sends error notifications

**Configuration Requirements**:

1. **Backend URL**: Update the HTTP request nodes to point to your backend:
   - Development: `http://localhost:8000`
   - Production: `https://your-backend-domain.com`

2. **Slack Integration** (Optional):
   - Configure Slack credentials in n8n
   - Update channel/webhook URLs in notification nodes
   - Remove notification nodes if Slack is not needed

3. **Schedule Timing**:
   - Current: 9 AM weekdays (`0 9 * * 1-5`)
   - Adjust cron expression as needed for your reporting schedule

## Setup Instructions

### 1. Import Workflow

1. Open n8n interface
2. Go to Workflows
3. Click "Import" 
4. Upload `meta-ads-daily-pull.json`
5. Activate the workflow

### 2. Configure Endpoints

Update HTTP request nodes with your actual backend URLs:

```json
{
  "url": "http://localhost:8000/api/webhook/n8n-trigger",
  // Change to production URL when deployed
}
```

### 3. Set Up Credentials

If using Slack notifications:
1. Go to n8n Credentials
2. Add Slack OAuth2 or Webhook credentials
3. Configure notification nodes to use these credentials

### 4. Test the Workflow

Run a manual test:
1. Click "Execute Workflow" in n8n
2. Check backend logs for data sync activity
3. Verify data appears in dashboard

## Webhook Endpoints

The workflow calls these backend endpoints:

- **Sync Trigger**: `POST /api/webhook/n8n-trigger`
  ```json
  {
    "trigger": "scheduled_sync",
    "target_date": "2024-08-18",
    "metadata": {
      "triggered_by": "n8n_schedule",
      "workflow_execution_id": "12345"
    }
  }
  ```

- **MTD Summary**: `GET /api/reports/month-to-date`

## Error Handling

The workflow includes comprehensive error handling:

- **Connection Failures**: Retries and error notifications
- **Backend Errors**: Captures error messages and logs
- **Slack Failures**: Workflow continues even if notifications fail

## Customization Options

### Schedule Changes

Modify the cron expression in the Schedule Trigger:

```javascript
// Current: Weekdays at 9 AM
"0 9 * * 1-5"

// Daily at 8 AM
"0 8 * * *"

// Twice daily (8 AM and 2 PM)
"0 8,14 * * *"
```

### Date Range Logic

The date calculator can be modified for different reporting periods:

```javascript
// Current: Month-to-date ending yesterday
const yesterday = new Date(today);
yesterday.setDate(today.getDate() - 1);

// Alternative: Current week
const startOfWeek = new Date(today);
startOfWeek.setDate(today.getDate() - today.getDay());
```

### Additional Workflows

Consider creating additional workflows for:

- **Weekly Reports**: Generate weekly summaries
- **Campaign Alerts**: Monitor performance thresholds
- **Monthly Aggregation**: End-of-month processing
- **Manual Sync**: On-demand data pulls

## Monitoring

Monitor workflow execution through:

1. **n8n Execution History**: Check for failed runs
2. **Backend Logs**: Monitor API calls and data processing
3. **Slack Notifications**: Real-time success/failure alerts
4. **Dashboard**: Verify data freshness

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**:
   - Check backend is running
   - Verify URL in HTTP request nodes
   - Check firewall/network settings

2. **Meta API Errors**:
   - Verify access token in backend .env
   - Check Meta API rate limits
   - Review backend logs for API errors

3. **Slack Notifications Not Working**:
   - Verify Slack credentials in n8n
   - Check channel permissions
   - Test with simple message first

4. **Date Range Issues**:
   - Check timezone settings in n8n
   - Verify date calculation logic
   - Test with manual date inputs
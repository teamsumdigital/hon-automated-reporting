# HON Automated Reporting - Database Issue Fix

## Problem Identified
✅ **Root Cause**: Database sync failing with "500: Failed to store data in database"

- Backend API: ✅ Healthy
- Meta API: ✅ Connected  
- Database: ❌ Sync failing at storage step

## Most Likely Causes

### 1. Database Schema Not Set Up (Most Likely)
The `campaign_data` table may not exist in your Supabase database.

**Fix**: Run database schema setup in Supabase:

1. Go to your Supabase dashboard
2. Open SQL Editor  
3. Copy and paste the contents of `database/schema.sql`
4. Click "Run" to create all tables

### 2. Wrong Supabase Credentials
The SUPABASE_URL or SUPABASE_SERVICE_KEY in Render might be incorrect.

**Fix**: Verify environment variables in Render:
- `SUPABASE_URL`: Should look like `https://xxxxx.supabase.co`
- `SUPABASE_SERVICE_KEY`: Should be the service role key (starts with `eyJ...`)

### 3. Database Permissions
The service key might not have insert permissions.

**Fix**: Ensure you're using the service role key, not the anon key.

## Quick Test Steps

1. **Manual database setup** (recommended first step):
   - Copy `database/schema.sql` contents
   - Paste into Supabase SQL Editor
   - Run to create tables

2. **Test sync again**:
   ```bash
   curl -X POST https://hon-automated-reporting.onrender.com/api/reports/sync
   ```

3. **Check if data appears**:
   ```bash
   curl https://hon-automated-reporting.onrender.com/api/reports/campaigns
   ```

## Expected Result
After fixing, you should see:
- Sync endpoint returns success message
- Campaigns endpoint returns data array
- Dashboard shows actual campaign metrics instead of zeros

## Need Help?
If the schema setup doesn't fix it, the issue is likely with the Supabase credentials in your Render environment variables.
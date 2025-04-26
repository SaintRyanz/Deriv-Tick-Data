# Deriv Index Tick Data Fetcher - GitHub Actions Setup

This guide explains how to set up your Deriv Index Tick Data Fetcher to run in the cloud using GitHub Actions, so you can collect data 24/7 without keeping your PC on.

## Setup Instructions

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in (or create an account if you don't have one)
2. Click on the "+" icon in the top right and select "New repository"
3. Name your repository (e.g., "deriv-tick-data")
4. Choose "Public" (free) or "Private" (requires GitHub Pro for Actions)
5. Click "Create repository"

### 2. Push Your Code to GitHub

Run these commands in your project directory:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### 3. Add Your API Token as a Secret

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `DERIV_API_TOKEN`
5. Value: Your Deriv API token
6. Click "Add secret"

### 4. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. You should see the "Fetch Deriv Tick Data" workflow
3. Click "Enable workflow"

The workflow will now run:
- Every 3 hours automatically (as configured in the YAML file)
- Whenever you manually trigger it from the Actions tab

## How It Works

1. **GitHub Actions** runs your data fetcher in the cloud on a schedule
2. The fetcher collects tick data and saves it to CSV files
3. The workflow commits and pushes the new data back to your GitHub repository
4. When you turn on your PC, you can sync the latest data using the `sync_from_github.py` script

## Syncing Data to Your Local Machine

When you want to download the latest data:

1. Open a command prompt in your project directory
2. Run:
   ```
   python sync_from_github.py
   ```

This script will:
- Pull the latest data from GitHub
- Show you which files have been updated
- Log the sync activity to `sync.log`

## Customizing the Schedule

To change how often the data fetcher runs:

1. Edit the `.github/workflows/fetch_tick_data.yml` file
2. Modify the `cron` expression in the `schedule` section
3. Commit and push your changes

Current schedule: `0 */3 * * *` (every 3 hours)

## Monitoring

You can monitor the data collection:

1. Go to the "Actions" tab in your GitHub repository
2. Click on the "Fetch Deriv Tick Data" workflow
3. You'll see all the runs, their status, and when they occurred
4. Click on any run to see detailed logs

## Troubleshooting

If the workflow fails:

1. Check the run logs in the Actions tab
2. Verify your API token is correct
3. Make sure your repository has write permissions for the workflow

## Data Storage Considerations

GitHub has storage limits:
- Free accounts: 500 MB soft limit, 1 GB hard limit
- If your data grows too large, consider:
  - Using Git LFS (Large File Storage)
  - Implementing a rotation policy to delete older data
  - Connecting to external storage (AWS S3, Google Cloud Storage)

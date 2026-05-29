# NIAT Insider Automation

Automatically generates and submits articles to NIAT Insider every 10 minutes using AI (Groq).

## Setup Instructions

### 1. Create a GitHub Repository

```bash
cd ~/Desktop/niat_automations
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/niat-automation.git
git push -u origin main
```

### 2. Add GitHub Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Add these 4 secrets:

| Secret Name            | Value                                           |
| ---------------------- | ----------------------------------------------- |
| `GROQ_API_KEY`         | Your Groq API key from https://console.groq.com |
| `ALERT_EMAIL_FROM`     | Your Gmail address                              |
| `ALERT_EMAIL_PASSWORD` | Your Gmail app password (not regular password)  |
| `ALERT_EMAIL_TO`       | Email to receive alerts                         |

### 3. Enable Workflows

- Go to Actions tab
- Click "I understand my workflows, go ahead and enable them"

## How It Works

- Runs **every 10 minutes** automatically via GitHub Actions (free tier: 144 runs/day)
- Generates unique article content using Groq AI
- Submits to NIAT Insider "Career & Wins" section
- Emails alerts on failures
- Logs all activity

## Features

✅ 24/7 automated submissions  
✅ AI-generated unique content  
✅ Error handling & retries  
✅ Email notifications on failure  
✅ Completely free

## Monitoring

- Check workflow runs: Go to Actions tab
- View logs: Click on run → scroll down
- Download logs: Artifacts section

## Notes

- GitHub Actions free tier allows ~10,000 minutes/month
- This script uses ~2-3 minutes per run
- So you can run ~3,333 times/month (plenty!)
- Persistent Firefox profile stored in logs

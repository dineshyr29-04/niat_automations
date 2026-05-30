# NIAT Insider Automation

Automatically generates and submits articles to NIAT Insider every 10 minutes using AI (Groq) with Playwright browser automation.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable

Export your Groq API key:

```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

Get your Groq API key from: https://console.groq.com

### 3. Run the Script

```bash
python niatinsider_automation.py
```

The script will:

- Launch Firefox browser (persistent session)
- Generate unique article content using Groq AI
- Submit to NIAT Insider "Career & Wins" section
- Wait 10 minutes and repeat
- Continue running until manually stopped

## How It Works

- Runs **every 10 minutes** in a continuous loop
- Uses **Groq AI** (llama-3.1-8b-instant) to generate:
  - Article title (career advancement focused)
  - Article subtitle
  - Article body (3-4 paragraphs)
- Uses **Playwright** to automate browser interactions:
  - Navigate to NIAT Insider contribution form
  - Fill in generated content
  - Submit article for review
- Includes error handling and automatic retry on failures

## Features

✅ Continuous automated submissions (every 10 minutes)  
✅ AI-generated unique content (Groq API)  
✅ Browser automation with Firefox (Playwright)  
✅ Error handling & automatic retry  
✅ Persistent Firefox session  
✅ Clean content formatting (removes markdown, quotes, etc.)  
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

from playwright.sync_api import sync_playwright
from groq import Groq
import time
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import traceback

URL = "https://www.niatinsider.com/contribute/write"

# Setup logging
log_dir = os.path.expanduser("~/niat_automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def send_alert_email(subject, body):
    """Send email alert on critical failures."""
    try:
        email_user = os.getenv("ALERT_EMAIL_FROM")
        email_password = os.getenv("ALERT_EMAIL_PASSWORD")
        email_to = os.getenv("ALERT_EMAIL_TO")
        
        if not all([email_user, email_password, email_to]):
            logger.warning("Email credentials not configured, skipping alert")
            return
        
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = f"[NIAT Automation Alert] {subject}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        logger.info("Alert email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")

def retry_with_backoff(func, max_retries=3, base_delay=5):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                raise

def clean_content(text):
    """Remove markdown formatting and clean up AI-generated content."""
    # Remove leading/trailing quotes
    text = text.strip('"\'')
    
    # Remove markdown bold and italic markers
    text = text.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
    
    # Remove markdown headers
    text = text.replace('# ', '').replace('## ', '').replace('### ', '')
    
    # Remove markdown list markers
    text = text.replace('- ', '').replace('* ', '')
    
    # Clean up extra whitespace
    text = ' '.join(text.split())
    
    return text

def generate_content():
    """Generate title, subtitle, and body content using Groq API about career & wins."""
    try:
        logger.info("Generating content...")
        
        # Generate title
        title_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": "Generate a compelling article title about career advancement and professional wins. Keep it concise (under 10 words). Just the title, no quotes."
                }
            ],
            temperature=0.7,
            max_tokens=50
        )
        title = title_response.choices[0].message.content.strip()
        title = clean_content(title)
        logger.info(f"Generated title: {title}")
        
        # Generate subtitle
        subtitle_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a compelling subtitle for an article about career wins. The article title is: '{title}'. Keep it concise (under 10 words). Just the subtitle, no quotes."
                }
            ],
            temperature=0.7,
            max_tokens=50
        )
        subtitle = subtitle_response.choices[0].message.content.strip()
        subtitle = clean_content(subtitle)
        logger.info(f"Generated subtitle: {subtitle}")
        
        # Generate body
        body_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"Write an article body (3-4 paragraphs) about career advancement and professional wins. Title: '{title}'. Subtitle: '{subtitle}'. Make it practical, inspiring, and actionable for professionals and students."
                }
            ],
            temperature=0.8,
            max_tokens=600
        )
        body = body_response.choices[0].message.content.strip()
        body = clean_content(body)
        logger.info("Generated body content successfully")
        
        return title, subtitle, body
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise

def submit_article():
    """Submit article with comprehensive error handling."""
    try:
        logger.info("Starting article submission process...")
        title, subtitle, body = generate_content()
        
        def attempt_submission():
            with sync_playwright() as p:
                logger.info("Launching Firefox...")
                context = p.firefox.launch_persistent_context(
                    user_data_dir="/tmp/firefox_profile",
                    headless=False
                )

                page = context.new_page()
                
                try:
                    logger.info(f"Navigating to {URL}")
                    page.goto(URL)

                    # Wait for page to fully load
                    logger.info("Waiting for page to load...")
                    page.wait_for_load_state("networkidle", timeout=20000)
                    page.wait_for_timeout(3000)

                    # Wait for the select element
                    logger.info("Waiting for form elements...")
                    page.wait_for_selector("select#section-select", timeout=20000, state="attached")

                    # Category dropdown - Career & Wins
                    logger.info("Selecting category...")
                    page.select_option(
                        "select#section-select",
                        value="a86e7f7e-3b3b-41fc-bcde-9fa246c5cb4a"
                    )

                    # Title field
                    logger.info("Filling title field...")
                    page.fill('.article-title-input', title)

                    # Subtitle field
                    logger.info("Filling subtitle field...")
                    page.fill('.article-subtitle-input', subtitle)

                    # Body field (contenteditable div)
                    logger.info("Filling body field...")
                    page.fill('.article-body-editor', body)

                    # Submit button
                    logger.info("Clicking submit button...")
                    page.click('button:has-text("Submit for Review")')

                    page.wait_for_timeout(5000)
                    logger.info("Article submitted successfully!")
                    
                finally:
                    context.close()
        
        # Attempt submission with retries
        retry_with_backoff(attempt_submission, max_retries=3, base_delay=10)
        logger.info("Submission completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"Failed to submit article: {str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        
        # Send email alert on failure
        send_alert_email(
            "Article Submission Failed",
            error_msg
        )
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("NIAT Insider Automation Started")
    logger.info(f"Logs will be saved to: {log_file}")
    logger.info("="*60)
    
    submission_count = 0
    failed_count = 0
    
    while True:
        try:
            logger.info(f"\n--- Submission #{submission_count + 1} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            if submit_article():
                submission_count += 1
                logger.info(f"Total successful submissions: {submission_count}")
            else:
                failed_count += 1
                logger.warning(f"Total failed submissions: {failed_count}")
            
            # Wait 10 minutes before next submission
            logger.info("Waiting 10 minutes before next submission...")
            time.sleep(600)
            
        except KeyboardInterrupt:
            logger.info("Automation stopped by user")
            logger.info(f"Final stats - Successful: {submission_count}, Failed: {failed_count}")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}\n{traceback.format_exc()}")
            send_alert_email(
                "Automation Process Crashed",
                f"Unexpected error in main loop:\n\n{traceback.format_exc()}"
            )
            # Wait before retry
            logger.info("Waiting 5 minutes before retry...")
            time.sleep(300)
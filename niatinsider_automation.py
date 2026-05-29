from playwright.sync_api import sync_playwright
from groq import Groq
import time
import os

URL = "https://www.niatinsider.com/contribute/write"

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    
    return title, subtitle, body

def submit_article():
    title, subtitle, body = generate_content()

    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            user_data_dir="/tmp/firefox_profile",
            headless=False
        )

        page = context.new_page()

        page.goto(URL)

        # Wait for page to fully load
        page.wait_for_load_state("networkidle", timeout=20000)

        page.wait_for_timeout(3000)

        # Wait for the select element to be available with longer timeout
        page.wait_for_selector("select#section-select", timeout=20000, state="attached")

        # Category dropdown - Career & Wins
        page.select_option(
            "select#section-select",
            value="a86e7f7e-3b3b-41fc-bcde-9fa246c5cb4a"
        )

        # Title field
        page.fill(
            '.article-title-input',
            title
        )

        # Subtitle field
        page.fill(
            '.article-subtitle-input',
            subtitle
        )

        # Body field (contenteditable div)
        page.fill(
            '.article-body-editor',
            body
        )

        # Submit button
        page.click(
            'button:has-text("Submit for Review")'
        )

        page.wait_for_timeout(5000)

        context.close()

while True:
    try:
        submit_article()
        print("Submission completed.")
    except Exception as e:
        print("Error:", e)

    # 10 minutes
    time.sleep(360)
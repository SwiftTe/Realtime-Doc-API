import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

def send_mention_email(user_email, document_title, commenter_name, comment_text, document_url):
    message = Mail(
        from_email="notifications@yourdomain.com",
        to_emails=user_email,
        subject=f"📌 You were mentioned in '{document_title}'",
        html_content=f"""
        <p>{commenter_name} mentioned you in a comment:</p>
        <blockquote>{comment_text}</blockquote>
        <a href="{document_url}">Open Document</a>
        """
    )
    
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Email error: {e}")
        return False

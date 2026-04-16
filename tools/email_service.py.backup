import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str):
    """
    Sends an email with a file attachment using SMTP settings from environment variables.
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
        raise ValueError("Missing SMTP configuration in environment variables.")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach file
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)
    elif attachment_path:
        print(f"Warning: Attachment path {attachment_path} does not exist.")

    # Send email
    print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
    try:
        # Add a 30 second timeout to avoid hanging the UI
        server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=30)
        server.set_debuglevel(1) # Enable debug output for terminal
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise e

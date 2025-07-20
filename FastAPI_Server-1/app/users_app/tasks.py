import smtplib
import ssl
from email.message import EmailMessage
from app.settings import logger, EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT, DEFAULT_FROM_EMAIL
from app.celery import celery

# Sending verification code
def send_mail(subject: str, message: str, user_emails: list[str]):
    port = int(EMAIL_PORT)
    smtp_server = EMAIL_HOST
    username = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = DEFAULT_FROM_EMAIL
    msg['To'] = user_emails # Supports List of email addresses
    msg.set_content(message)

    try:
        # Handling SSL and TLS based on the port number
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(username, password)
                server.send_message(msg)
        elif port == 587:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()  # Secure the connection with TLS
                server.login(username, password)
                server.send_message(msg)
        else:
            logger.error(f"Invalid port number: {port}. Use 465 (SSL) or 587 (TLS).")
            return

        logger.info("Email sent successfully.")

    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")

@celery.task(name="send_verification_email")
def send_verification_email(email: str, verification_code: str):
    subject = "Your Email Verification Code"
    message = f"""
    Dear User,

    Thank you for registering. Please use the following code to verify your email:

    Verification Code: {verification_code}

    This code will expire in 10 minutes.

    Best regards,
    Team Voiceagent
    """
    send_mail(subject, message, [email])
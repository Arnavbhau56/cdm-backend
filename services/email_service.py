# Email service: sends founder questions as a numbered plain-text email via Gmail SMTP + STARTTLS.

import smtplib
import os
from email.mime.text import MIMEText


def send_founder_questions(recipient: str, startup_name: str, questions: list):
    """Send numbered founder questions to the given recipient via Gmail SMTP."""
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        raise ValueError('GMAIL_USER and GMAIL_APP_PASSWORD must be set in environment variables')

    numbered = '\n'.join(f'{i + 1}. {q}' for i, q in enumerate(questions))
    body = f'Founder Questions — {startup_name}\n\n{numbered}'

    msg = MIMEText(body, 'plain')
    msg['Subject'] = f'Founder Questions — {startup_name}'
    msg['From'] = gmail_user
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [recipient], msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        raise Exception(f'Gmail authentication failed. Please check your GMAIL_APP_PASSWORD. Error: {str(e)}')
    except smtplib.SMTPException as e:
        raise Exception(f'SMTP error occurred: {str(e)}')
    except Exception as e:
        raise Exception(f'Failed to send email: {str(e)}')


def send_custom_email(recipient: str, startup_name: str, body: str):
    """Send custom email to the given recipient via Gmail SMTP."""
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        raise ValueError('GMAIL_USER and GMAIL_APP_PASSWORD must be set in environment variables')

    msg = MIMEText(body, 'plain')
    msg['Subject'] = f'Re: {startup_name}'
    msg['From'] = gmail_user
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [recipient], msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        raise Exception(f'Gmail authentication failed. Please check your GMAIL_APP_PASSWORD. Error: {str(e)}')
    except smtplib.SMTPException as e:
        raise Exception(f'SMTP error occurred: {str(e)}')
    except Exception as e:
        raise Exception(f'Failed to send email: {str(e)}')

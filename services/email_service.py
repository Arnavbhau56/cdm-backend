# Email service: sends founder questions as a numbered plain-text email via Gmail SMTP + STARTTLS.

import smtplib
import os
from email.mime.text import MIMEText


def send_founder_questions(recipient: str, startup_name: str, questions: list):
    """Send numbered founder questions to the given recipient via Gmail SMTP."""
    gmail_user = os.environ['GMAIL_USER']
    gmail_password = os.environ['GMAIL_APP_PASSWORD']

    numbered = '\n'.join(f'{i + 1}. {q}' for i, q in enumerate(questions))
    body = f'Founder Questions — {startup_name}\n\n{numbered}'

    msg = MIMEText(body, 'plain')
    msg['Subject'] = f'Founder Questions — {startup_name}'
    msg['From'] = gmail_user
    msg['To'] = recipient

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, [recipient], msg.as_string())

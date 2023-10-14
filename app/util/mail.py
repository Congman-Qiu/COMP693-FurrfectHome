#testing gmail: pgtrackerlincoln@gmail.com
#testing gmail password: pgtracker2023!
#Gmail App-Specific Passwords: rrgptiicdprpklme

from email.message import EmailMessage
from app.models.email_model import Email
from app.services import accounts
import ssl
import smtplib

def send_email(email: Email):

    email_sender = 'pgtrackerlincoln@gmail.com'  # 'pgtrackerlincoln@gmail.com'
    email_password = 'rrgptiicdprpklme'
    email.email_body = email.email_body + '\n\nOriginal recipient: ' + email.email_to

    # temporarily set 'TO' email address to our own email until the production version is ready
    # appended the original 'TO' email address to the body of the email beforehand
    # you can update this email address to your own email if you want to test it out
    # for that simply navigate to <appliaction_path>/config/email

    test_email = accounts.get_test_email()

    email.email_to = test_email

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email.email_to
    em['Subject'] = email.email_subject
    em.set_content(email.email_body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email.email_to, em.as_string())

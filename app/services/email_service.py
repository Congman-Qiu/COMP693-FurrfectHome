
from app.models.email_model import Email
from app.util.mail import send_email

# send email
# takes email arguments, sets to email object, and sends email


def email(to, subject, body):
    email = Email()

    email.email_to = to
    email.email_subject = subject
    email.email_body = body

    send_email(email)

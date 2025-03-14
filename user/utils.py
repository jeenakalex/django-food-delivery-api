from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_email):
    """Send email to the given recipient"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}") 
        return False

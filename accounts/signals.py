
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from accounts.tasks import send_email

@receiver(post_save, sender=CustomUser)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = "Welcome to Online shop"
        message = f'Hi {instance.first_name}, Welcome to Online shop. Enjoy products and qualities'
        recipient = instance.email
        send_email.delay(subject, message, recipient)

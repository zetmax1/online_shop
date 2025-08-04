from django.core.mail import send_mail

from config.celery import app


@app.task()
def send_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'zokhidjonyuta@gmail.com',
        [recipient_list],
    )


@app.task
def send_reset_code(recipient_list, code):
    subject = 'Code for reset password'
    message = f"Your new code is: {code}"
    send_mail(subject,
              message,
              'zokhidjonyuta@gmail.com',
              [recipient_list],
              fail_silently=False
              )

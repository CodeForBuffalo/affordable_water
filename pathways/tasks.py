from __future__ import absolute_import
from celery import shared_task
from celery.decorators import task
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task  # Use this decorator to make this an asyncronous function
def send_email(subject, recipient_list, template_name, **kwargs):
    messages = list()

    for recipient in recipient_list:
        # Build context
        context = {'first_name' : recipient[0] }

        # Render HTML content to string
        html_content = render_to_string(template_name=template_name, context=context)

        # Build EmailMessage with stripped HTML tags
        msg = mail.message.EmailMultiAlternatives(subject=subject, body=strip_tags(html_content), to=[recipient[1]])

        # Attach alternative with HTML content
        msg.attach_alternative(html_content, "text/html")

        # Add msg to messages list
        messages.append(msg)
    
    # Django implicitly opens and closes connection afterwards
    connection = mail.get_connection()
    connection.send_messages(messages)
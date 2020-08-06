from __future__ import absolute_import
from celery import shared_task
from celery.decorators import task
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Application, Document, ForgivenessApplication, EmailCommunication

@shared_task  # Use this decorator to make this an asyncronous function
def send_email(subject, recipient_list, template_name, **kwargs):
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
        msg.send()

def send_automatic_email(email_address, email_type, subject, template_name, recipient_list):
    # Filter to applicant's email address
    email_coms = EmailCommunication.objects.filter(email_address=email_address)

    # Maps to True if applicant's email address has received this email type before
    has_received_email_type_before = {
        'discount_receive': email_coms.filter(discount_application_received=True).exists(),
        'discount_enroll': email_coms.filter(enrolled_in_discount_program=True).exists(),
        'amnesty_receive': email_coms.filter(amnesty_application_received=True).exists(),
        'amnesty_enroll': email_coms.filter(enrolled_in_amnesty_program=True).exists(),
    }

    # If they haven't received the email before
    if not has_received_email_type_before[email_type]:
        # Send email task
        send_email.delay(subject=subject, recipient_list=recipient_list, template_name=template_name)
        
        defaults_for_create = {
            'discount_receive': {'email_address': email_address, 'discount_application_received': True},
            'discount_enroll': {'email_address': email_address, 'enrolled_in_discount_program': True},
            'amnesty_receive': {'email_address': email_address, 'amnesty_application_received': True},
            'amnesty_enroll': {'email_address': email_address, 'enrolled_in_amnesty_program': True},
        }

        # Get or create EmailCommunication object
        email_com, created = EmailCommunication.objects.get_or_create(
            email_address__iexact=email_address,
            defaults=defaults_for_create[email_type]
        )
        # Change and save EmailCommunication object if it already existed
        if not created:
            if email_type == 'discount_receive':
                email_com.discount_application_received = True
            elif email_type == 'discount_enroll':
                email_com.enrolled_in_discount_program = True
            elif email_type == 'amnesty_receive':
                email_com.amnesty_application_received = True
            elif email_type == 'amnesty_enroll':
                email_com.enrolled_in_amnesty_program = True
            else:
                raise ValueError("Invalid email_type")
            email_com.save()
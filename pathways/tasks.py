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

def send_confirmation_email_after_discount_enrolled(app):
    subject = 'You have been successfully enrolled in the Buffalo Water Affordability Program'
    template_name = 'pathways/emails/discount_enrolled.html'
    recipient_list = [(app.first_name, app.email_address)]

    # If they haven't received enrollment email before
    if not EmailCommunication.objects.filter(enrolled_in_discount_program=True).exists():
        # Send email task
        send_email.delay(subject=subject, recipient_list=recipient_list, template_name=template_name)
        
        # Get or create EmailCommunication object
        email_com, created = EmailCommunication.objects.get_or_create(
            email_address__iexact=app.email_address,
            defaults={'email_address': app.email_address, 'enrolled_in_discount_program': True}
        )
        # Change and save EmailCommunication object if it already existed
        if not created:
            email_com.enrolled_in_discount_program = True
            email_com.save()

def send_confirmation_email_after_amnesty_enrolled(app):
    subject = 'You have been successfully enrolled in the Buffalo Water Amnesty Program'
    template_name = 'pathways/emails/amnesty_enrolled.html'
    recipient_list = [(app.first_name, app.email_address)]
    
    # If they haven't received enrollment email before
    if not EmailCommunication.objects.filter(enrolled_in_amnesty_program=True).exists():
        # Send email task
        send_email.delay(subject=subject, recipient_list=recipient_list, template_name=template_name)
        
        # Get or create EmailCommunication object
        email_com, created = EmailCommunication.objects.get_or_create(
            email_address__iexact=app.email_address,
            defaults={'email_address': app.email_address, 'enrolled_in_amnesty_program': True}
        )
        # Change and save EmailCommunication object if it already existed
        if not created:
            email_com.enrolled_in_amnesty_program = True
            email_com.save()

def send_received_confirmation_on_discount_application(app):
    subject = 'We received your application for the Buffalo Water Affordability Program'
    template_name = 'pathways/emails/discount_confirmation_no_docs_now.html'
    recipient_list = [(app.first_name, app.email_address)]

    # If they haven't received confirmation email before
    if not EmailCommunication.objects.filter(discount_application_received=True).exists():
        # Send email task
        send_email.delay(subject=subject, recipient_list=recipient_list, template_name=template_name)
        
        # Get or create EmailCommunication object
        email_com, created = EmailCommunication.objects.get_or_create(
            email_address__iexact=app.email_address,
            defaults={'email_address': app.email_address, 'discount_application_received': True}
        )
        # Change and save EmailCommunication object if it already existed
        if not created:
            email_com.discount_application_received = True
            email_com.save()

def send_received_confirmation_on_amnesty_application(app):
    subject = 'We received your application for the Buffalo Water Amnesty Program'
    template_name = 'pathways/emails/amnesty_confirmation.html'
    recipient_list = [(app.first_name, app.email_address)]

    # If they haven't received confirmation email before
    if not EmailCommunication.objects.filter(amnesty_application_received=True).exists():
        # Send email task
        send_email.delay(subject=subject, recipient_list=recipient_list, template_name=template_name)
        
        # Get or create EmailCommunication object
        email_com, created = EmailCommunication.objects.get_or_create(
            email_address__iexact=app.email_address,
            defaults={'email_address': app.email_address, 'amnesty_application_received': True}
        )
        # Change and save EmailCommunication object if it already existed
        if not created:
            email_com.amnesty_application_received = True
            email_com.save()
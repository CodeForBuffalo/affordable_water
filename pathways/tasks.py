from __future__ import absolute_import
from celery import shared_task
from .management.commands.send_email import send_email_message
import requests

@shared_task  # Use this decorator to make this a asyncronous function
def send_email(subject, recipient_list_mass, email_template):
    send_email_message(subject=subject, recipient_list_mass=recipient_list_mass, email_template=email_template)
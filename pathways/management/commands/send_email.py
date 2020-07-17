from django.core.management.base import BaseCommand, CommandError
from pathways.tasks import send_email

class Command(BaseCommand):
    help = 'Sends email'

    def handle(self, *args, **kwargs):
        if(all(x in kwargs for x in ['subject', 'recipient_list', 'email_template'])):
            subject = kwargs['subject']
            recipient_list = kwargs['recipient_list']
            email_template = kwargs['email_template']
            send_email(subject=subject, recipient_list=recipient_list, email_template=email_template)


from django.core.management.base import BaseCommand
from pathways.tasks import send_email

class Command(BaseCommand):
    help = 'Sends email'

    def handle(self, *args, **kwargs):
        if(all(x in kwargs for x in ['subject', 'recipient_list', 'template_name'])):
            subject = kwargs['subject']
            recipient_list = kwargs['recipient_list']
            template_name = kwargs['template_name']
            send_email(subject=subject, recipient_list=recipient_list, template_name=template_name)
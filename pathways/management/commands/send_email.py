from django.core.management.base import BaseCommand, CommandError
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from affordable_water.settings import EMAIL_HOST_USER

class Command(BaseCommand):
    help = 'Sends email'

    def handle(self, *args, **kwargs):
        if(all(x in kwargs for x in ['subject', 'recipient_list_mass', 'email_template'])):
            subject = kwargs['subject']
            recipient_list_mass = kwargs['recipient_list_mass']
            email_template = kwargs['email_template']
            send_email_message(subject=subject, recipient_list_mass=recipient_list_mass, email_template=email_template)

def send_email_message(subject, recipient_list_mass, email_template):
    from_email = "Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>"

    connection = mail.get_connection()
    messages = list()

    for recipient in recipient_list_mass:
        html_content = render_to_string('pathways/emails/'+ email_template +'.html', { 'first_name' : recipient[0] })
        msg = mail.message.EmailMultiAlternatives(subject, strip_tags(html_content), from_email, [recipient[1]])
        msg.attach_alternative(html_content, "text/html")
        messages.append(msg)
    
    connection.send_messages(messages)
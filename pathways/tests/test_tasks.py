from django.test import TestCase
from django.urls import reverse
from pathways.tasks import send_email
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class SendEmailTests(TestCase):
    def test_send_amnesty_confirmation_email(self):
        subject = 'We received your application for the Buffalo Water Amnesty Program'
        recipient_list = [('Your first name', 'to@example.com')]
        template_name = 'pathways/emails/amnesty_confirmation.html'

        send_email(subject=subject, recipient_list=recipient_list, template_name=template_name)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, subject)

        # Verify that the from_email is correct
        self.assertEqual(mail.outbox[0].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')

        # Verify that the recipient is correct
        self.assertEqual(mail.outbox[0].to, ['to@example.com'])

        # Verify that the template is correct
        self.assertIn('We have successfully received your application for the Buffalo Water Amnesty Program.', mail.outbox[0].body)
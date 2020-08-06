from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from pathways.models import Application, ForgivenessApplication, EmailCommunication
from django.core import mail

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class DiscountEmailSignalTest(TestCase):
    def setUp(self):
        activate('en')

    def test_received_discount_email_sent(self):
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        app = Application.objects.create(
            household_size=1, has_household_benefits=True, first_name='Test', last_name='User',
            rent_or_own='own', street_address='123 Main St', zip_code='14202', phone_number='716-555-5555',
            email_address='testing@getwaterwisebuffalo.org', account_holder='me', account_first='Test', 
            account_last='User', legal_agreement=True, signature='Test User', status='new'
            )
        
        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact=app.email_address).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'We received your application for the Buffalo Water Affordability Program')
        self.assertEqual(mail.outbox[0].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')
        self.assertEqual(mail.outbox[0].to, ['testing@getwaterwisebuffalo.org'])
        self.assertIn('We received your application', mail.outbox[0].body)

    def test_enroll_discount_email_sent(self):
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        app = Application.objects.create(
            household_size=1, has_household_benefits=True, first_name='Test', last_name='User',
            rent_or_own='own', street_address='123 Main St', zip_code='14202', phone_number='716-555-5555',
            email_address='testing@getwaterwisebuffalo.org', account_holder='me', account_first='Test', 
            account_last='User', legal_agreement=True, signature='Test User', status='new'
            )
        
        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact=app.email_address).exists())

        app = Application.objects.get(email_address='testing@getwaterwisebuffalo.org')
        app.status = 'enrolled'
        app.save()

        # Verify that enrolled email has been sent as well
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'You have been successfully enrolled in the Buffalo Water Affordability Program')
        self.assertEqual(mail.outbox[1].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')
        self.assertEqual(mail.outbox[1].to, ['testing@getwaterwisebuffalo.org'])
        self.assertIn('Water Affordability Program has been approved', mail.outbox[1].body)

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AmnestyEmailSignalTest(TestCase):
    def setUp(self):
        activate('en')

    def test_received_amnesty_email_sent(self):
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        app = ForgivenessApplication.objects.create(
            first_name='Test', last_name='User', street_address='123 Main St', zip_code='14202', phone_number='716-555-5555',
            email_address='testingtwo@getwaterwisebuffalo.org', status='new'
            )

        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact=app.email_address).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'We received your application for the Buffalo Water Amnesty Program')
        self.assertEqual(mail.outbox[0].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')
        self.assertEqual(mail.outbox[0].to, ['testingtwo@getwaterwisebuffalo.org'])
        self.assertIn('We have successfully received your application for the Buffalo Water Amnesty Program. Here is what you can expect next.', mail.outbox[0].body)

    def test_enroll_amnesty_email_sent(self):
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        app = ForgivenessApplication.objects.create(
            first_name='Test', last_name='User', street_address='123 Main St', zip_code='14202', phone_number='716-555-5555',
            email_address='testingtwo@getwaterwisebuffalo.org', status='new'
            )

        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact=app.email_address).exists())
        self.assertEqual(len(mail.outbox), 1)

        app = ForgivenessApplication.objects.get(email_address='testingtwo@getwaterwisebuffalo.org')
        app.status = 'enrolled'
        app.save()

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'You have been successfully enrolled in the Buffalo Water Amnesty Program')
        self.assertEqual(mail.outbox[1].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')
        self.assertEqual(mail.outbox[1].to, ['testingtwo@getwaterwisebuffalo.org'])
        self.assertIn('Your application for the Buffalo Water Amnesty Program has been approved and you have been successfully enrolled!', mail.outbox[1].body)
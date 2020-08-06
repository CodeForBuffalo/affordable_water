from django.test import LiveServerTestCase, TestCase, Client, override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from pathways.models import Application

# model tests
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ApplicationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.app_1 = Application.objects.create(
            household_size=1,
            has_household_benefits=False,
            annual_income=10000,
            first_name='John',
            last_name='Doe',
            middle_initial='M',
            rent_or_own='rent',
            street_address = '123 Main St',
            zip_code = '14202',
            apartment_unit = 'A',
            phone_number = '7163334444',
            email_address = 'testing@email.com',
            account_holder = 'me',
            account_first = 'John',
            account_middle = 'M',
            account_last = 'Doe',
            legal_agreement = True,
            signature = 'John M Doe'
            )

    def setUp(self):
        self.app_1.refresh_from_db()

    def tearDown(self):
        pass

    def test_application_self_string(self):
        expected = '1 - Doe at 123 Main St'
        self.assertEqual(self.app_1.__str__(), expected, msg=f'app_1 self string expected {expected} but got {self.app_1.__str__()}')

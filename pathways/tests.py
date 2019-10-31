from django.test import LiveServerTestCase, TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .models import Application

# model tests
class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.app_1 = Application.objects.create(
            household_size=1,
            hasHouseholdBenefits=False,
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
        expected = '1 (7163334444)'
        self.assertEqual(self.app_1.__str__(), expected, msg=f'app_1 self string expected {expected} but got {self.app_1.__str__()}')

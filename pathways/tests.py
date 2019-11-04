from django.test import LiveServerTestCase, TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from .models import Application
from .forms import *

# view tests
class TestViews(TestCase):
    def setUp(self):
        activate('en')

    def test_homepage(self):
        response = self.client.get(reverse('pathways-home'))
        self.assertContains(response, text="class=\"template--homepage\"", status_code=200)

    def test_apply(self):
        session = self.client.session
        session['dummykey'] = True
        session.save()
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        # checks that the dummykey was saved correctly
        self.assertIn('dummykey', list(session.keys()))
        session = self.client.session
        response = self.client.get(reverse('pathways-apply'))
        self.assertContains(response, text=_("Here's how Affordable Water works."), status_code=200)
        # Checks if session keys are deleted
        self.assertEqual(len(session.keys()), 0, f"Expected 0 but got {len(session.items())}. Keys include {list(session.keys())}.")

# form tests
class FormTests(TestCase):
    def setUp(self):
        activate('en')

    def test_HouseholdForm(self):
        for i in range(1,9):
            form_data = {'household_size':i}
            form = HouseholdForm(data=form_data)
            self.assertTrue(form.is_valid(), msg=f"Form is invalid for household_size {i}.")
        form = HouseholdForm(data={})
        self.assertFalse(form.is_valid(), msg=f"Form with empty data should be invalid.")
        self.assertIn(_("Select your household size."), form.errors['household_size'])

    def test_ExactIncomeForm(self):
        form = ExactIncomeForm(data={})
        self.assertFalse(form.is_valid(), msg=f"Form with empty data should be invalid.")
        self.assertIn(_("Select a pay period"), form.errors['pay_period'])
        self.assertIn(_("Be sure to provide your job income before taxes"), form.errors['income'])


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

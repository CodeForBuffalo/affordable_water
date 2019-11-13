from django.test import TestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _

# view tests
class HomeViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-home'), follow=True)
        self.assertTemplateUsed(response, 'pathways/home.html')

    def test_view_uses_template_homepage_css_class(self):
        response = self.client.get(reverse('pathways-home'), follow=True)
        self.assertContains(response, text="class=\"template--homepage\"")

class ApplyViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/overview.html')
    
    def test_view_clears_existing_session_keys(self):
        session = self.client.session
        session['testkey'] = True
        session.save()
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        response = self.client.get(reverse('pathways-apply'), follow=True)
        # Checks if session keys are deleted
        self.assertEqual(len(session.keys()), 0, f"Expected 0 but got {len(session.items())}. Keys include {list(session.keys())}.")

class HouseholdSizeViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-household-size'), follow=True)
        self.assertIs(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-household-size'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/household-size.html')

    def test_submit_form_valid(self):
        response = self.client.post(reverse('pathways-apply-household-size'), data={'household_size': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/apply/household-benefits/')
        self.assertIn('active_app', self.client.session.keys())
        self.assertIn('household_size', self.client.session.keys())
        self.assertEqual(self.client.session['household_size'], '1')

class HouseholdBenefitsViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['household_size'] = 1
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-household-benefits'), follow=True)
        self.assertIs(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-household-benefits'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/household-benefits.html')

    def test_submit_form_valid(self):
        for hasHouseholdBenefits in [True, False]:
            response = self.client.post(reverse('pathways-apply-household-benefits'), data={'hasHouseholdBenefits': hasHouseholdBenefits})
            self.assertEqual(response.status_code, 302)
            if hasHouseholdBenefits:
                self.assertEqual(response.url, '/apply/eligibility/')
            else:
                self.assertEqual(response.url, '/apply/income-methods/')
            self.assertIn('hasHouseholdBenefits', self.client.session.keys())
            self.assertEqual(self.client.session['hasHouseholdBenefits'], str(hasHouseholdBenefits))

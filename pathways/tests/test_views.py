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
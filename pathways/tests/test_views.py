from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from pathways.models import ForgivenessApplication, EmailCommunication
from django.core import mail

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

class ApplyOverviewAssistanceViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/assistance-overview.html')

class ForgiveOverviewViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['first_name'] = 'Test'
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-forgive-overview'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-forgive-overview'), follow=True)
        self.assertTemplateUsed(response, 'pathways/forgive/water-amnesty.html')

    def test_view_deletes_previous_session_keys_and_adds_forgive_step(self):
        response = self.client.get(reverse('pathways-forgive-overview'), follow=True)
        self.assertNotIn('first_name', self.client.session.keys())
        self.assertIn('forgive_step', self.client.session.keys())
        self.assertEqual(self.client.session['forgive_step'], 'overview')

class ForgiveCityResidentViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-city-resident'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-city-resident'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/city-resident.html')

    def test_redirect_on_submit(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        for city_resident in [True, False]:
            response = self.client.post(reverse('pathways-forgive-city-resident'), data={'city_resident': city_resident}, follow=True, secure=True)
            if city_resident:
                self.assertRedirects(response, reverse('pathways-forgive-additional-questions'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-non-resident'), fetch_redirect_response=False)
    
    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        for k in session.keys():
            print(k)
        response = self.client.get(reverse('pathways-forgive-city-resident'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-overview'), fetch_redirect_response=False)
        self.assertNotIn('forgive_step', self.client.session.keys(), msg=f"Keys include {list(session.keys())}.")

class ForgiveAdditionalQuestionsViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-additional-questions'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-additional-questions'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/forgive/additional-questions.html')

    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        session.save()
        response = self.client.get(reverse('pathways-forgive-additional-questions'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-overview'), fetch_redirect_response=False)

class ForgiveResidentInfoViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-resident-info'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-resident-info'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/info-form.html')
    
    def test_redirect_on_submit(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.post(reverse('pathways-forgive-resident-info'), 
        data={
            'first_name': 'Test', 'last_name': 'User', 'middle_initial': 'R', 
            'street_address': '123 Main St', 'phone_number': '555-555-5555', 'zip_code': 14202
            }, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-refer'), fetch_redirect_response=False)
        self.assertEqual('filled_application', self.client.session['forgive_step'])

    def test_session_saved_on_submit(self):
        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.post(reverse('pathways-forgive-resident-info'), 
        data={
            'first_name': 'Test', 'last_name': 'User', 'middle_initial': 'R', 
            'street_address': '123 Main St', 'phone_number': '555-555-5555', 'zip_code': 14202
            }, follow=True, secure=True)
        self.assertIn('first_name', self.client.session.keys())
        self.assertEqual(self.client.session['first_name'], 'Test')
        self.assertIn('last_name', self.client.session.keys())
        self.assertEqual(self.client.session['last_name'], 'User')
        self.assertIn('middle_initial', self.client.session.keys())
        self.assertEqual(self.client.session['middle_initial'], 'R')
        self.assertIn('street_address', self.client.session.keys())
        self.assertEqual(self.client.session['street_address'], '123 Main St')
        self.assertIn('phone_number', self.client.session.keys())
        self.assertEqual(self.client.session['phone_number'], '555-555-5555')
        self.assertIn('zip_code', self.client.session.keys())
        self.assertEqual(self.client.session['zip_code'], '14202')
    
    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        session.save()
        response = self.client.get(reverse('pathways-forgive-resident-info'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-overview'), fetch_redirect_response=False)

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ForgiveReviewApplicationViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-review-application'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-review-application'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/forgive/review-application.html')

    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        session.save()
        response = self.client.get(reverse('pathways-forgive-review-application'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-overview'), fetch_redirect_response=False)

    def test_view_does_not_redirect_on_dispatch_with_submit_application_as_if_pressing_back_button(self):
        session = self.client.session
        session['forgive_step'] = 'submit_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-review-application'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pathways/forgive/review-application.html')

    def test_redirect_on_submit(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['street_address'] = '123 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'testing@getwaterwisebuffalo.org'
        session.save()
        response = self.client.post(reverse('pathways-forgive-review-application'), data={'submit_application': True}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-confirmation'), fetch_redirect_response=False)
        self.assertEqual('submit_application', self.client.session['forgive_step'])

    def test_session_saved_on_submit(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['street_address'] = '123 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'testing@getwaterwisebuffalo.org'
        session.save()
        response = self.client.post(reverse('pathways-forgive-review-application'), data={'submit_application': True}, follow=True, secure=True)
        self.assertIn('forgive_step', self.client.session.keys())
        self.assertEqual(self.client.session['forgive_step'], 'submit_application')

    def test_forgiveness_application_created(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['street_address'] = '123 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'testing@getwaterwisebuffalo.org'
        session.save()

        response = self.client.post(reverse('pathways-forgive-review-application'), data={'submit_application': True}, follow=True, secure=True)

        self.assertTrue({'forgive_step', 'first_name', 'last_name', 'middle_initial', 'street_address', 'zip_code', 'phone_number', 'email_address'}.issubset(self.client.session.keys()))
        self.assertTrue(ForgivenessApplication.objects.filter(email_address__iexact='testing@getwaterwisebuffalo.org', street_address='123 Main St').exists())

    def test_email_sent_after_forgiveness_application_created(self):
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['street_address'] = '12345 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'testing@getwaterwisebuffalo.org'
        session.save()

        # Verify pre-post state
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(EmailCommunication.objects.filter(email_address__iexact='testing@getwaterwisebuffalo.org', amnesty_application_received=True).exists())

        response = self.client.post(reverse('pathways-forgive-review-application'), data={'submit_application': True}, follow=True, secure=True)

        # Verify that an email message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct
        self.assertEqual(mail.outbox[0].subject, 'We received your application for the Buffalo Water Amnesty Program')

        # Verify that the from_email is correct
        self.assertEqual(mail.outbox[0].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')

        # Verify that the recipient is correct
        self.assertEqual(mail.outbox[0].to, ['testing@getwaterwisebuffalo.org'])

        # Verify that the template is correct
        self.assertIn('Here is what you can expect next', mail.outbox[0].body)

        # Verify EmailCommunication object has been recorded
        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact='testing@getwaterwisebuffalo.org', amnesty_application_received=True).exists())

class ForgiveConfirmationViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        session['forgive_step'] = 'submit_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-confirmation'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        session = self.client.session
        session['forgive_step'] = 'submit_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-confirmation'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/forgive/confirmation.html')

    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        session.save()
        response = self.client.get(reverse('pathways-forgive-confirmation'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-overview'), fetch_redirect_response=False)
    
    def test_view_redirects_on_dispatch_without_forgive_step_in_session(self):
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        session['forgive_step'] = 'filled_application'
        session.save()
        response = self.client.get(reverse('pathways-forgive-confirmation'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-resident-info'), fetch_redirect_response=False)

        session = self.client.session
        session['forgive_step'] = 'overview'
        session.save()
        response = self.client.get(reverse('pathways-forgive-confirmation'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-forgive-resident-info'), fetch_redirect_response=False)

class ApplyDiscountViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-discount-overview'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-discount-overview'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/discount-overview.html')
    
    def test_view_clears_existing_session_keys(self):
        session = self.client.session
        session['testkey'] = True
        session.save()
        # a new SessionStore is created every time this property is accessed
        session = self.client.session
        response = self.client.get(reverse('pathways-apply-discount-overview'), follow=True)
        # Checks if session keys are deleted
        self.assertEqual(len(session.keys()), 0, f"Expected 0 but got {len(session.items())}. Keys include {list(session.keys())}.")

class CityResidentViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-city-resident'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-city-resident'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/city-resident.html')

    def test_redirect_on_submit(self):
        for city_resident in [True, False]:
            response = self.client.post(reverse('pathways-apply-city-resident'), data={'city_resident': city_resident}, follow=True, secure=True)
            if city_resident:
                self.assertRedirects(response, reverse('pathways-apply-household-size'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-non-resident'), fetch_redirect_response=False)

class HouseholdSizeViewTest(TestCase):
    def setUp(self):
        activate('en')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-household-size'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-household-size'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/household-size.html')

    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-household-size'), data={'household_size': 1}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-household-benefits'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-household-size'), data={'household_size': 1}, follow=True, secure=True)
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
        response = self.client.get(reverse('pathways-apply-household-benefits'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-household-benefits'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/household-benefits.html')

    def test_redirect_on_submit(self):
        for has_household_benefits in [True, False]:
            response = self.client.post(reverse('pathways-apply-household-benefits'), data={'has_household_benefits': has_household_benefits}, follow=True, secure=True)
            if has_household_benefits:
                self.assertRedirects(response, reverse('pathways-apply-eligibility'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-household-contributors'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for has_household_benefits in [True, False]:
            response = self.client.post(reverse('pathways-apply-household-benefits'), data={'has_household_benefits': has_household_benefits}, follow=True, secure=True)
            self.assertIn('has_household_benefits', self.client.session.keys())
            self.assertEqual(self.client.session['has_household_benefits'], str(has_household_benefits))

class DispatchViewTest(TestCase):
    def setUp(self):
        activate('en')
    
    def test_url_without_active_app_session_key(self):
        response = self.client.get(reverse('pathways-apply-household-benefits'), follow=False, secure=True)
        self.assertRedirects(response, reverse('pathways-home'), fetch_redirect_response=False)

class HouseholdContributorsViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 1
        session['has_household_benefits'] = False
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-household-contributors'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-household-contributors'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/household-contributors.html')
    
    def test_redirect_on_submit(self):
        for household_contributors in [1,2,3,4]:
            response = self.client.post(reverse('pathways-apply-household-contributors'), data={'household_contributors': household_contributors}, follow=True, secure=True)
            if household_contributors == 1:
                self.assertRedirects(response, reverse('pathways-apply-job-status'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-income'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for household_contributors in [1,2,3,4]:
            response = self.client.post(reverse('pathways-apply-household-contributors'), data={'household_contributors': household_contributors}, follow=True, secure=True)
            self.assertIn('household_contributors', self.client.session.keys())
            self.assertEqual(self.client.session['household_contributors'], str(household_contributors))
            if household_contributors > 1:
                self.assertIn('income_method', self.client.session.keys())
                self.assertEqual(self.client.session['income_method'], 'estimate')

class JobStatusViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 1
        session['has_household_benefits'] = False
        session['household_contributors'] = 1
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-job-status'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-job-status'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/job-status.html')
    
    def test_redirect_on_submit(self):
        for has_job in [True, False]:
            response = self.client.post(reverse('pathways-apply-job-status'), data={'has_job': str(has_job)}, follow=True, secure=True)
            self.assertRedirects(response, reverse('pathways-apply-self-employment'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for has_job in [True, False]:
            response = self.client.post(reverse('pathways-apply-job-status'), data={'has_job': str(has_job)}, follow=True, secure=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('has_job', self.client.session.keys())
            self.assertEqual(self.client.session['has_job'], str(has_job))

class SelfEmploymentViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 1
        session['has_household_benefits'] = False
        session['household_contributors'] = 1
        session['has_job'] = 'True'
        session.save()
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-self-employment'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-self-employment'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/self-employment.html')

    def test_redirect_on_submit(self):
        session = self.client.session
        for has_job in [True, False]:
            session['has_job'] = has_job
            session.save()
            response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': True}, follow=True, secure=True)
            self.assertRedirects(response, reverse('pathways-apply-number-of-jobs'), fetch_redirect_response=False)

        session = self.client.session
        session['has_job'] = False
        session.save()
        response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': False}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-other-income-sources'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for is_self_employed in [True, False]:
            response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': str(is_self_employed)}, follow=True, secure=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('is_self_employed', self.client.session.keys())
            self.assertEqual(self.client.session['is_self_employed'], str(is_self_employed))

class OtherIncomeSourcesViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['has_job'] = True
        session['is_self_employed'] = True
        session.save()
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-other-income-sources'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-other-income-sources'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/other-income-sources.html')

    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': True}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-non-job-income'), fetch_redirect_response=False)

        response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': False}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False,)

    def test_session_saved_on_submit(self):
        for has_other_income in [True, False]:
            response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': has_other_income}, follow=True, secure=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('has_other_income', self.client.session.keys())
            self.assertEqual(self.client.session['has_other_income'], str(has_other_income))

class NumberOfJobsViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-number-of-jobs'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-number-of-jobs'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/number-of-jobs.html')
    
    def test_redirect_on_submit(self):
        for number_of_jobs in range(1,9):
            response = self.client.post(reverse('pathways-apply-number-of-jobs'), data={'number_of_jobs': number_of_jobs}, follow=True, secure=True)
            if number_of_jobs == 1:
                self.assertRedirects(response, reverse('pathways-apply-income-methods'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-income'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for number_of_jobs in range(1,9):
            response = self.client.post(reverse('pathways-apply-number-of-jobs'), data={'number_of_jobs': number_of_jobs}, follow=True, secure=True)
            self.assertIn('number_of_jobs', self.client.session.keys())
            self.assertEqual(self.client.session['number_of_jobs'], str(number_of_jobs))
            if number_of_jobs > 1:
                self.assertIn('income_method', self.client.session.keys())
                self.assertEqual(self.client.session['income_method'], 'estimate')

class NonJobIncomeViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['has_job'] = False
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['annual_income'] = 12000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-non-job-income'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-non-job-income'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/non-job-income.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-non-job-income'), data={'non_job_income': 15}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-non-job-income'), data={'non_job_income': 15}, follow=True, secure=True)
        self.assertIn('non_job_income', self.client.session.keys())
        self.assertEqual(self.client.session['non_job_income'], 15)

class IncomeMethodsViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['has_job'] = True
        session['number_of_jobs'] = 1
        session['is_self_employed'] = False
        session['has_other_income'] = False
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-income-methods'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-income-methods'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/income-methods.html')
    
    def test_redirect_on_submit(self):
        for income_method in ['exact', 'hourly', 'estimate']:
            response = self.client.post(reverse('pathways-apply-income-methods'), data={'income_method': income_method}, follow=True, secure=True)
            self.assertRedirects(response, reverse('pathways-apply-income'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for income_method in ['exact', 'hourly', 'estimate']:
            response = self.client.post(reverse('pathways-apply-income-methods'), data={'income_method': income_method}, follow=True, secure=True)
            self.assertIn('income_method', self.client.session.keys())
            self.assertEqual(self.client.session['income_method'], income_method)

class IncomeViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['has_job'] = True
        session['number_of_jobs'] = 1
        session['is_self_employed'] = False
        session['has_other_income'] = False
        session.save()

    def test_view_url_exists_at_desired_location(self):
        session = self.client.session
        for income_method in ['exact', 'hourly', 'estimate']:
            session['income_method'] = income_method
            session.save()
            response = self.client.get(reverse('pathways-apply-income'), follow=True, secure=True)
            self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        session = self.client.session
        for income_method in ['exact', 'hourly', 'estimate']:
            session['income_method'] = income_method
            session.save()
            response = self.client.get(reverse('pathways-apply-income'), follow=True, secure=True)
            self.assertTemplateUsed(response, 'pathways/apply/'+ income_method +'-income.html')
    
    def test_redirect_on_submit(self):
        session = self.client.session
        # exact
        session['income_method'] = 'exact'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 500, 'pay_period': 'weekly'}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-other-income-sources'), fetch_redirect_response=False)

        # hourly
        session['income_method'] = 'hourly'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 15, 'pay_period': 40}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-other-income-sources'), fetch_redirect_response=False)

        # estimate
        session['income_method'] = 'estimate'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 2000, 'pay_period': 'semimonthly'}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-other-income-sources'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        session = self.client.session
        # exact
        session['income_method'] = 'exact'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 500, 'pay_period': 'weekly'}, follow=True, secure=True)
        self.assertIn('income', self.client.session.keys())
        self.assertIn('pay_period', self.client.session.keys())
        self.assertIn('annual_income', self.client.session.keys())
        self.assertEqual(self.client.session['income'], 500)
        self.assertEqual(self.client.session['pay_period'], 'weekly')
        self.assertEqual(self.client.session['annual_income'], 26000)

        # hourly
        session['income_method'] = 'hourly'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 15, 'pay_period': 40}, follow=True, secure=True)
        self.assertIn('income', self.client.session.keys())
        self.assertIn('pay_period', self.client.session.keys())
        self.assertIn('annual_income', self.client.session.keys())
        self.assertEqual(self.client.session['income'], 15)
        self.assertEqual(self.client.session['pay_period'], 40)
        self.assertEqual(self.client.session['annual_income'], 31200)

        # estimate
        session['income_method'] = 'estimate'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 2000, 'pay_period': 'semimonthly'}, follow=True, secure=True)
        self.assertIn('income', self.client.session.keys())
        self.assertIn('pay_period', self.client.session.keys())
        self.assertIn('annual_income', self.client.session.keys())
        self.assertEqual(self.client.session['income'], 2000)
        self.assertEqual(self.client.session['pay_period'], 'semimonthly')
        self.assertEqual(self.client.session['annual_income'], 48000)

class ReviewEligibilityViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_job'] = True
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-review-eligibility'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-review-eligibility'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/review-eligibility.html')

class EligibilityViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_household_benefits'] = False
        session['has_job'] = True
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-eligibility'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-eligibility'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/eligibility.html')

class AdditionalQuestionsViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-additional-questions'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-additional-questions'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/additional-questions.html')

class ResidentInfoViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['has_job'] = False
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['annual_income'] = 12000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-resident-info'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-resident-info'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/resident-info.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-resident-info'), 
        data={
            'first_name': 'Test', 'last_name': 'User', 'middle_initial': 'R', 
            'rent_or_own': 'rent', 'account_holder': 'landlord',
            }, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-account-holder'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-resident-info'), 
        data={
            'first_name': 'Test', 'last_name': 'User', 'middle_initial': 'R', 
            'rent_or_own': 'rent', 'account_holder': 'landlord',
            }, follow=True, secure=True)
        self.assertIn('first_name', self.client.session.keys())
        self.assertEqual(self.client.session['first_name'], 'Test')
        self.assertIn('last_name', self.client.session.keys())
        self.assertEqual(self.client.session['last_name'], 'User')
        self.assertIn('middle_initial', self.client.session.keys())
        self.assertEqual(self.client.session['middle_initial'], 'R')
        self.assertIn('rent_or_own', self.client.session.keys())
        self.assertEqual(self.client.session['rent_or_own'], 'rent')
        self.assertIn('account_holder', self.client.session.keys())
        self.assertEqual(self.client.session['account_holder'], 'landlord')

class AccountHolderViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-account-holder'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-account-holder'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/info-form.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-account-holder'), 
        data={
            'account_first': 'Land', 'account_last': 'Lord', 'account_middle': 'O',
            }, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-address'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-account-holder'), 
        data={
            'account_first': 'Land', 'account_last': 'Lord', 'account_middle': 'O',
            }, follow=True, secure=True)
        self.assertIn('account_first', self.client.session.keys())
        self.assertEqual(self.client.session['account_first'], 'Land')
        self.assertIn('account_last', self.client.session.keys())
        self.assertEqual(self.client.session['account_last'], 'Lord')
        self.assertIn('account_middle', self.client.session.keys())
        self.assertEqual(self.client.session['account_middle'], 'O')

class AddressViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-address'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-address'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/info-form.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-address'), 
        data={
            'street_address': '123 Main St', 'apartment_unit': 'Upper', 'zip_code': '14202',
            }, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-contact-info'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-address'), 
        data={
            'street_address': '123 Main St', 'apartment_unit': 'Upper', 'zip_code': '14202',
            }, follow=True, secure=True)
        self.assertIn('street_address', self.client.session.keys())
        self.assertEqual(self.client.session['street_address'], '123 Main St')
        self.assertIn('apartment_unit', self.client.session.keys())
        self.assertEqual(self.client.session['apartment_unit'], 'Upper')
        self.assertIn('zip_code', self.client.session.keys())
        self.assertEqual(self.client.session['zip_code'], '14202')

class ContactInfoViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-contact-info'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-contact-info'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/info-form.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-contact-info'), 
        data={
            'phone_number': '716-555-5555', 'email_address': 'example@example.com',
            }, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-application'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-contact-info'), 
        data={
            'phone_number': '716-555-5555', 'email_address': 'example@example.com',
            }, follow=True, secure=True)
        self.assertIn('phone_number', self.client.session.keys())
        self.assertEqual(self.client.session['phone_number'], '716-555-5555')
        self.assertIn('email_address', self.client.session.keys())
        self.assertEqual(self.client.session['email_address'], 'example@example.com')

class AccountNumberViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_household_benefits'] = False
        session['has_job'] = True
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-account-number'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-account-number'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/info-form.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'account_number': '123456789'}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-application'), fetch_redirect_response=False)

        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'has_account_number': False}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-application'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'account_number': '123456789'}, follow=True, secure=True)
        self.assertIn('account_number', self.client.session.keys())
        self.assertEqual(self.client.session['account_number'], '123456789')

        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'has_account_number': False}, follow=True, secure=True)
        self.assertIn('has_account_number', self.client.session.keys())
        self.assertEqual(self.client.session['has_account_number'], False)

class ReviewApplicationViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_household_benefits'] = False
        session['has_job'] = True
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-review-application'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-review-application'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/review-application.html')

class LegalViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_household_benefits'] = False
        session['has_job'] = True
        session['is_self_employed'] = False
        session['has_other_income'] = True
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-legal'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-legal'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/legal.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-legal'),
        data={'legal_agreement': True}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-refer'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-legal'), 
        data={'legal_agreement': True}, follow=True, secure=True)
        self.assertIn('legal_agreement', self.client.session.keys())
        self.assertEqual(self.client.session['legal_agreement'], True)

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SignatureViewTest(TestCase):
    def setUp(self):
        activate('en')
        session = self.client.session
        session['active_app'] = True
        session['household_size'] = 2
        session['has_household_benefits'] = 'False'
        session['has_job'] = 'True'
        session['is_self_employed'] = 'False'
        session['has_other_income'] = 'True'
        session['income'] = 500
        session['income_method'] = 'exact'
        session['pay_period'] = 'weekly'
        session['annual_income'] = 26000
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['rent_or_own'] = 'rent'
        session['street_address'] = '1234 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'example@example.com'
        session['account_holder'] = 'me'
        session['account_first'] = 'Test'
        session['account_last'] = 'User'
        session['account_middle'] = 'R'
        session['has_account_number'] = 'False'
        session['legal_agreement'] = 'True'
        session.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-signature'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-signature'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'pathways/apply/signature.html')
    
    def test_redirect_on_submit(self):
        response = self.client.post(reverse('pathways-apply-signature'),
        data={'signature': 'Test User'}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-documents-overview'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-signature'), 
        data={'signature': 'Test User'}, follow=True, secure=True)
        self.assertIn('signature', self.client.session.keys())
        self.assertEqual(self.client.session['signature'], 'Test User')
        self.assertIn('app_id', self.client.session.keys())

    def test_email_confirmation_sent_on_submit(self):
        # Verify pre-post state
        self.assertEqual(EmailCommunication.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        # Verify boolean logic for email check
        self.assertFalse(EmailCommunication.objects.filter(email_address__iexact='testing@getwaterwisebuffalo.org', discount_application_received=True).exists())

        response = self.client.post(reverse('pathways-apply-signature'), data={'signature': 'Test User'}, follow=True, secure=True)

        # Verify that an email message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct
        self.assertEqual(mail.outbox[0].subject, 'We received your application for the Buffalo Water Affordability Program')

        # Verify that the from_email is correct
        self.assertEqual(mail.outbox[0].from_email, 'Get Water Wise Buffalo <hello@getwaterwisebuffalo.org>')

        # Verify that the recipient is correct
        self.assertEqual(mail.outbox[0].to, ['example@example.com'])

        # Verify that the template is correct
        self.assertIn('you can submit your documents', mail.outbox[0].body)

        # Verify email communication has been sent
        self.assertTrue(EmailCommunication.objects.filter(email_address__iexact='example@example.com', discount_application_received=True).exists())
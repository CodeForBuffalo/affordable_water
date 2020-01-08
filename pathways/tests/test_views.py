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
        for hasHouseholdBenefits in [True, False]:
            response = self.client.post(reverse('pathways-apply-household-benefits'), data={'hasHouseholdBenefits': hasHouseholdBenefits}, follow=True, secure=True)
            if hasHouseholdBenefits:
                self.assertRedirects(response, reverse('pathways-apply-eligibility'), fetch_redirect_response=False)
            else:
                self.assertRedirects(response, reverse('pathways-apply-household-contributors'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        for hasHouseholdBenefits in [True, False]:
            response = self.client.post(reverse('pathways-apply-household-benefits'), data={'hasHouseholdBenefits': hasHouseholdBenefits}, follow=True, secure=True)
            self.assertIn('hasHouseholdBenefits', self.client.session.keys())
            self.assertEqual(self.client.session['hasHouseholdBenefits'], str(hasHouseholdBenefits))

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
        session['hasHouseholdBenefits'] = False
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
        session['hasHouseholdBenefits'] = False
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
        session['hasHouseholdBenefits'] = False
        session['household_contributors'] = 1
        session['has_job'] = True
        session.save()
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('pathways-apply-self-employment'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('pathways-apply-self-employment'), follow=True)
        self.assertTemplateUsed(response, 'pathways/apply/self-employment.html')

    def test_redirect_on_submit(self):
        for is_self_employed in [True, False]:
            response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': str(is_self_employed)}, follow=True, secure=True)
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
        for has_other_income in [True, False]:
            response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': has_other_income}, follow=True, secure=True)
            self.assertRedirects(response, reverse('pathways-apply-number-of-jobs'),
                fetch_redirect_response=False,
                msg_prefix=f"has_other_income {has_other_income} has_job {self.client.session['has_job']} and is_self_employed {self.client.session['is_self_employed']}")

        session = self.client.session
        session['has_job'] = False
        session['is_self_employed'] = False
        session.save()

        # has other income, does NOT have job, is NOT self-employed
        response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': True}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-non-job-income'), fetch_redirect_response=False)

        # does NOT have other income, does NOT have job, is NOT self-employed
        response = self.client.post(reverse('pathways-apply-other-income-sources'), data={'has_other_income': False}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False)

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
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False)

        # hourly
        session['income_method'] = 'hourly'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 15, 'pay_period': 40}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False)

        # estimate
        session['income_method'] = 'estimate'
        session.save()
        response = self.client.post(reverse('pathways-apply-income'), data={'income': 2000, 'pay_period': 'semimonthly'}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-eligibility'), fetch_redirect_response=False)

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
        session['hasHouseholdBenefits'] = False
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
        self.assertRedirects(response, reverse('pathways-apply-resident-info'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-resident-info'), data={'non_job_income': 15}, follow=True, secure=True)
        self.assertIn('non_job_income', self.client.session.keys())
        self.assertEqual(self.client.session['non_job_income'], 15)
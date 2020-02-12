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
        for has_job in ['True', 'False']:
            self.client.session['has_job'] = has_job
            self.client.session.save()
            response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': 'True'}, follow=True, secure=True)
            self.assertRedirects(response, reverse('pathways-apply-number-of-jobs'), fetch_redirect_response=False)

        self.client.session['has_job'] = 'False'
        self.client.session.save()
        response = self.client.post(reverse('pathways-apply-self-employment'), data={'is_self_employed': 'False'}, follow=True, secure=True)
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
        self.assertRedirects(response, reverse('pathways-apply-account-number'), fetch_redirect_response=False)

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
        data={'hasAccountNumber': False}, follow=True, secure=True)
        self.assertRedirects(response, reverse('pathways-apply-review-application'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'account_number': '123456789'}, follow=True, secure=True)
        self.assertIn('account_number', self.client.session.keys())
        self.assertEqual(self.client.session['account_number'], '123456789')

        response = self.client.post(reverse('pathways-apply-account-number'), 
        data={'hasAccountNumber': False}, follow=True, secure=True)
        self.assertIn('hasAccountNumber', self.client.session.keys())
        self.assertEqual(self.client.session['hasAccountNumber'], False)

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
        self.assertRedirects(response, reverse('pathways-apply-signature'), fetch_redirect_response=False)

    def test_session_saved_on_submit(self):
        response = self.client.post(reverse('pathways-apply-legal'), 
        data={'legal_agreement': True}, follow=True, secure=True)
        self.assertIn('legal_agreement', self.client.session.keys())
        self.assertEqual(self.client.session['legal_agreement'], True)

class SignatureViewTest(TestCase):
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
        session['first_name'] = 'Test'
        session['last_name'] = 'User'
        session['middle_initial'] = 'R'
        session['rent_or_own'] = 'rent'
        session['street_address'] = '123 Main St'
        session['zip_code'] = '14202'
        session['phone_number'] = '716-555-5555'
        session['email_address'] = 'example@example.com'
        session['account_holder'] = 'me'
        session['account_first'] = 'Test'
        session['account_last'] = 'User'
        session['account_middle'] = 'R'
        session['hasAccountNumber'] = False
        session['legal_agreement'] = True
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
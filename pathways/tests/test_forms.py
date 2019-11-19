from django.test import TestCase
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from pathways import forms

class HouseholdSizeFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.HouseholdSizeForm(data={})
        self.assertIn(_("Select your household size."), form.errors['household_size'])

    def test_help_text_correct(self):
        form = forms.HouseholdSizeForm(data={})
        self.assertEqual(form['household_size'].help_text, _("Typically how many people you regularly share living expenses with, including yourself. If you live with them, include children under 21, spouses/partners, and parents."))

class HouseholdContributorsFormTest(TestCase):
    def test_valid_form_inputs(self):
        for contributors in range(1,9):
            form = forms.HouseholdContributorsForm(data={'household_contributors': contributors})
            self.assertTrue(form.is_valid(), msg=f"Contributors {contributors} expected to be valid, form errors {form.errors}")
            self.assertEqual(form.cleaned_data['household_contributors'], str(contributors))

class JobStatusFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.JobStatusForm(data={})
        self.assertIn(_("Select your employment status."), form.errors['has_job'])

    def test_help_text_correct(self):
        form = forms.JobStatusForm(data={})
        self.assertEqual(form['has_job'].help_text, _("Make sure to include self-employed work."))

    def test_valid_form_inputs(self):
        for has_job in [True, False]:
            form = forms.JobStatusForm(data={'has_job': has_job})
            self.assertTrue(form.is_valid(), msg=f"Has_job {has_job} expected to be valid, form errors {form.errors}")
            self.assertEqual(form.cleaned_data['has_job'], str(has_job))

class SelfEmploymentFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.SelfEmploymentForm(data={})
        self.assertIn(_("Select your self-employment status."), form.errors['is_self_employed'])

    def test_valid_form_inputs(self):
        for is_self_employed in [True, False]:
            form = forms.SelfEmploymentForm(data={'is_self_employed': is_self_employed})
            self.assertTrue(form.is_valid(), msg=f"is_self_employed {is_self_employed} expected to be valid, form errors {form.errors}")
            self.assertEqual(form.cleaned_data['is_self_employed'], str(is_self_employed))

class OtherIncomeSourcesFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.OtherIncomeSourcesForm(data={})
        self.assertIn(_("Indicate whether you get any money from other sources."), form.errors['has_other_income'])

    def test_valid_form_inputs(self):
        for has_other_income in [True, False]:
            form = forms.OtherIncomeSourcesForm(data={'has_other_income': has_other_income})
            self.assertTrue(form.is_valid(), msg=f"has_other_income {has_other_income} expected to be valid, form errors {form.errors}")
            self.assertEqual(form.cleaned_data['has_other_income'], str(has_other_income))

class NumberOfJobsFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.NumberOfJobsForm(data={})
        self.assertIn(_("Select how many jobs you currently have."), form.errors['number_of_jobs'])

    def test_valid_form_inputs(self):
        for number_of_jobs in range(1,13):
            form = forms.NumberOfJobsForm(data={'number_of_jobs': number_of_jobs})
            self.assertTrue(form.is_valid(), msg=f"number_of_jobs {number_of_jobs} expected to be valid, form errors {form.errors}")
            self.assertEqual(form.cleaned_data['number_of_jobs'], str(number_of_jobs))

class NonJobIncomeFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.NonJobIncomeForm(data={})
        self.assertIn(_("Be sure to provide your income from other sources."), form.errors['non_job_income'])

    def test_valid_form_inputs(self):
        for non_job_income in [15.0, 3000, 0.01]:
            form = forms.NonJobIncomeForm(data={'non_job_income': non_job_income})
            self.assertTrue(form.is_valid(), msg=f"non_job_income {non_job_income} expected to be valid, form errors {form.errors}")

    def test_invalid_form_inputs(self):
        for non_job_income in [-15]:
            form = forms.NonJobIncomeForm(data={'non_job_income': non_job_income})
            self.assertFalse(form.is_valid(), msg=f"non_job_income {non_job_income} expected to be valid, form errors {form.errors}")

class ExactIncomeFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.ExactIncomeForm(data={})
        self.assertIn(_("Be sure to provide your income before taxes"), form.errors['income'])
        self.assertIn(_("Select a pay period"), form.errors['pay_period'])

    def test_valid_form_inputs(self):
        for income in [15.0, 3000, 0.01]:
            form = forms.ExactIncomeForm(data={'pay_period': 'weekly', 'income': income})
            self.assertTrue(form.is_valid(), msg=f"Income {income} expected to be valid. Form errors {form.errors}")
    
    def test_invalid_form_inputs(self):
        inputs = [-15]
        for income in inputs:
            form = forms.ExactIncomeForm(data={'pay_period': 'weekly', 'income': income})
            self.assertFalse(form.is_valid(), msg=f"Income {income} expected to be invalid. Form errors {form.errors}")

class HourlyIncomeFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.HourlyIncomeForm(data={})
        self.assertIn(_("Be sure to provide an hourly wage."), form.errors['income'])
        self.assertIn(_("Be sure to provide hours a week."), form.errors['pay_period'])
    
    def test_valid_form_inputs(self):
        for income in [15, 1, 3000, 45]:
            form = forms.HourlyIncomeForm(data={'pay_period': 40, 'income': income})
            self.assertTrue(form.is_valid(), msg=f"Income {income} expected to be valid. Form errors {form.errors}")
        
        for pay_period in [1, 15, 30, 40, 80]:
            form = forms.HourlyIncomeForm(data={'pay_period': pay_period, 'income': 20})
            self.assertTrue(form.is_valid(), msg=f"Pay_period {pay_period} expected to be valid. Form errors {form.errors}")
    
    def test_invalid_form_inputs(self):
        for income in [-15, 0]:
            form = forms.HourlyIncomeForm(data={'pay_period': 40, 'income': income})
            self.assertFalse(form.is_valid(), msg=f"Income {income} expected to be invalid. Form errors {form.errors}")
        
        for pay_period in [0, -15, 169]:
            form = forms.HourlyIncomeForm(data={'pay_period': pay_period, 'income': 15})
            self.assertFalse(form.is_valid(), msg=f"Pay_period {pay_period} expected to be invalid. Form errors {form.errors}")

class EstimateIncomeFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.EstimateIncomeForm(data={})
        self.assertIn(_("Be sure to provide a household income."), form.errors['income'])
        self.assertIn(_("Select how often your household makes this amount."), form.errors['pay_period'])
    
    def test_valid_form_inputs(self):
        for income in [15, 1, 3000, 45]:
            form = forms.EstimateIncomeForm(data={'pay_period': 'weekly', 'income': income})
            self.assertTrue(form.is_valid(), msg=f"Income {income} expected to be valid. Form errors {form.errors}")
        
        for pay_period in ['weekly', 'biweekly','semimonthly', 'monthly']:
            form = forms.EstimateIncomeForm(data={'pay_period': pay_period, 'income': 20})
            self.assertTrue(form.is_valid(), msg=f"Pay_period {pay_period} expected to be valid. Form errors {form.errors}")
    
    def test_invalid_form_inputs(self):
        for income in [-15]:
            form = forms.EstimateIncomeForm(data={'pay_period': 'weekly', 'income': income})
            self.assertFalse(form.is_valid(), msg=f"Income {income} expected to be invalid. Form errors {form.errors}")
        
        form = forms.EstimateIncomeForm(data={'pay_period': 'weekly'})
        self.assertFalse(form.is_valid(), msg=f"Form with empty income expected to be invalid. Form errors {form.errors}")

class ResidentInfoFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.ResidentInfoForm(data={})
        self.assertIn(_("Make sure to provide a first name."), form.errors['first_name'])
        self.assertIn(_("Make sure to provide a last name."), form.errors['last_name'])
        self.assertIn(_("Make sure to indicate whether you own or rent."), form.errors['rent_or_own'])
        self.assertIn(_("Make sure to indicate who officially pays the water bill."), form.errors['account_holder'])

class AddressFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.AddressForm(data={})
        self.assertIn(_("Make sure to provide a street address."), form.errors['street_address'])
        self.assertIn(_("Make sure to provide a 5 digit ZIP code."), form.errors['zip_code'])
    
    def test_valid_form_inputs(self):
        for address in ['123 Main St','456 Delaware']:
            form = forms.AddressForm(data={'street_address':address,'zip_code':14000})
            self.assertTrue(form.is_valid(), msg=f"AddressForm street_address {address} expected to be valid, form errors {form.errors}")
        for zip_code in [14202]:
            form = forms.AddressForm(data={'street_address':'123 Main St','zip_code':zip_code})
            self.assertTrue(form.is_valid(), msg=f"AddressForm zip_code {zip_code} expected to be valid, form errors {form.errors}")

    def test_invalid_form_inputs(self):
        for address in ['Ferry St','789']:
            form = forms.AddressForm(data={'street_address':address,'zip_code':14000})
            self.assertFalse(form.is_valid(), msg=f"AddressForm street_address {address} expected to be invalid, form errors {form.errors}")

        for zip_code in [123456, 4321]:
            form = forms.AddressForm(data={'street_address':'123 Main St','zip_code': zip_code})
            self.assertFalse(form.is_valid(), msg=f"AddressForm zip_code {zip_code} expected to be invalid, form errors {form.errors}")

class ContactInfoFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.ContactInfoForm(data={})
        self.assertIn(_("Make sure to provide a valid phone number."), form.errors['phone_number'])

        form = forms.ContactInfoForm(data={'phone_number': '71634565789123456'})
        self.assertIn(_("Please use a valid 10 digit phone number such as 716-555-5555."), form.errors['phone_number'])

    def test_valid_form_inputs(self):
        for phone_number in [7163334444, '716-333-4444', '(716)3334444', '(716) 333 4444', '(716)-333-4444']:
            form = forms.ContactInfoForm(data={'phone_number': phone_number})
            self.assertTrue(form.is_valid(), msg=f"ContactInfoForm phone_number {phone_number} expected to be valid, form errors {form.errors}")

        for email in ['example@example.com']:
            form in forms.ContactInfoForm(data={'phone_number': '716-555-5555', 'email_address': email})
            self.assertTrue(form.is_valid(), msg=f"ContactInfoForm email_address {email} expected to be valid, form errors {form.errors}")
    
    def test_invalid_form_inputs(self):
        for phone_number in [71633355555, '71633355555', '(716-3465-12345-', '71634565789123456']:
            form = forms.ContactInfoForm(data={'phone_number': phone_number})
            self.assertFalse(form.is_valid(), msg=f"ContactInfoForm phone_number {phone_number} expected to be invalid, form errors {form.errors}")
            
        form = forms.ContactInfoForm(data={'email_address':'example@example.com'})
        self.assertFalse(form.is_valid(), msg=f"ContactInfoForm with empty data for phone_number should be invalid.")

class AccountHolderFormTest(TestCase):
    def test_error_messages_correct(self):
        form = forms.AccountHolderForm(data={})
        self.assertIn(_("Make sure to provide a first name."), form.errors['account_first'])
        self.assertIn(_("Make sure to provide a last name."), form.errors['account_last'])
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Application, Document, ForgivenessApplication

# Register your models here.

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    pass

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

@admin.register(Application)
class ApplicationAdmin(SimpleHistoryAdmin):
    inlines = [
        DocumentInline,
    ]
    list_display = (
        '__str__', 'date_created', 'full_name', 'account_name', 'rent_or_own', 
        'street_address', 'apartment_unit', 'zip_code', 'household_size', 
        'has_household_benefits', 'has_residence_documents', 'has_eligible_documents'
    )

    def full_name(self, obj):
        if obj.middle_initial == '':
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.first_name + ' ' + obj.middle_initial + ' ' + obj.last_name

    def account_name(self, obj):
        return obj.account_first + ' ' + obj.account_middle + ' ' + obj.account_last

    def date_created(self, obj):
        return obj.history.all()[0].history_date

    def has_residence_documents(self, obj):
        residence_count = Document.objects.filter(application=obj, doc_type='residence').count()
        return residence_count > 0
    has_residence_documents.boolean = True
    has_residence_documents.description = 'Residence documents'

    def has_eligible_documents(self, obj):
        income_count = Document.objects.filter(application=obj, doc_type='income').count()
        benefits_count = Document.objects.filter(application=obj, doc_type='benefits').count()
        return income_count + benefits_count > 0
    has_eligible_documents.boolean = True
    has_eligible_documents.description = 'Income or benefits documents'

@admin.register(ForgivenessApplication)
class ForgivenessApplicationAdmin(SimpleHistoryAdmin):
    list_display = [
        '__str__', 'date_created', 'full_name', 
        'street_address', 'apartment_unit', 'zip_code',
        'phone_number', 'email_address',
        'status'
    ]

    list_editable = ['status']

    list_filter = ['status']

    list_per_page = 12

    def date_created(self, obj):
        return obj.history.all()[0].history_date

    def full_name(self, obj):
        if obj.middle_initial == '':
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.first_name + ' ' + obj.middle_initial + ' ' + obj.last_name

class ListFilter(admin.SimpleListFilter):
    pass

admin.site.site_header = "GetWaterWiseBuffalo Admin"
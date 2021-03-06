from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from pathways.models import Application, Document, ForgivenessApplication, EmailCommunication

# Register your models here.

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    pass


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0


@admin.register(Application)
class ApplicationAdmin(SimpleHistoryAdmin):
    inlines = [DocumentInline,]
    actions = ['make_enrolled', 'make_denied']
    list_display = [
        '__str__', 'date_created', 'full_name', 'account_name', 
        'rent_or_own', 'street_address', 'apt_unit', 'zip_code',
        'phone_number', 'discount_amount', 'status'
    ]
    list_editable = ['status']
    list_filter = ['status']

    def make_enrolled(self, request, queryset):
        for app in queryset:
            app.status = 'enrolled'
            app.save()
    make_enrolled.short_description = "Enroll selected Discount Applications"
    make_enrolled.allowed_permissions = ('change',)

    def make_denied(modeladmin, request, queryset):
        for app in queryset:
            app.status = 'denied'
            app.save()
    make_denied.short_description = "Deny selected Discount Applications"
    make_denied.allowed_permissions = ('change',)

    def apt_unit(self, obj):
        return obj.apartment_unit

    def full_name(self, obj):
        if obj.middle_initial == '':
            return obj.first_name + ' ' + obj.last_name
        return obj.first_name + ' ' + obj.middle_initial + ' ' + obj.last_name

    def account_name(self, obj):
        return obj.account_first + ' ' + obj.account_middle + ' ' + obj.account_last

    def date_created(self, obj):
        return obj.history.all()[0].history_date

    def has_residence_docs(self, obj):
        residence_count = Document.objects.filter(application=obj, doc_type='residence').count()
        return residence_count > 0
    has_residence_docs.boolean = True
    has_residence_docs.description = 'Residence documents'

    def has_eligible_docs(self, obj):
        income_count = Document.objects.filter(application=obj, doc_type='income').count()
        benefits_count = Document.objects.filter(application=obj, doc_type='benefits').count()
        return income_count + benefits_count > 0
    has_eligible_docs.boolean = True
    has_eligible_docs.description = 'Income or benefits documents'


@admin.register(ForgivenessApplication)
class ForgivenessApplicationAdmin(SimpleHistoryAdmin):
    actions = ['make_enrolled', 'make_denied']
    list_display = [
        '__str__', 'date_created', 'full_name', 'street_address', 'apt_unit',
        'zip_code', 'phone_number', 'email_address', 'status'
    ]
    list_editable = ['status']
    list_filter = ['status']
    list_per_page = 12

    def make_enrolled(modeladmin, request, queryset):
        for app in queryset:
            app.status = 'enrolled'
            app.save()

    make_enrolled.short_description = "Enroll selected Amnesty Applications"
    make_enrolled.allowed_permissions = ('change',)

    def make_denied(modeladmin, request, queryset):
        for app in queryset:
            app.status = 'denied'
            app.save()

    make_denied.short_description = "Deny selected Amnesty Applications"
    make_denied.allowed_permissions = ('change',)

    def apt_unit(self, obj):
        return obj.apartment_unit

    def date_created(self, obj):
        return obj.history.all()[0].history_date

    def full_name(self, obj):
        if obj.middle_initial == '':
            return obj.first_name + ' ' + obj.last_name
        return obj.first_name + ' ' + obj.middle_initial + ' ' + obj.last_name


@admin.register(EmailCommunication)
class EmailCommunicationAdmin(SimpleHistoryAdmin):
    readonly_fields = [
        'email_address',
        'discount_application_received', 
        'amnesty_application_received', 
        'enrolled_in_amnesty_program', 
        'enrolled_in_discount_program',
    ]

    list_display = [
        'email_address',
        'discount_application_received', 
        'amnesty_application_received', 
        'enrolled_in_amnesty_program', 
        'enrolled_in_discount_program',
    ]
    
    list_filter = [
        'email_address',
        'discount_application_received', 
        'amnesty_application_received', 
        'enrolled_in_amnesty_program', 
        'enrolled_in_discount_program',
    ]


admin.site.site_header = "GetWaterWiseBuffalo Admin"
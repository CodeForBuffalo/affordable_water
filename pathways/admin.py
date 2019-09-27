from django.contrib import admin
from .models import Application, Income, Document

# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('legal_agreement','signature','income_photo')
        return self.readonly_fields

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('application',)
        return self.readonly_fields

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('application',)
        return self.readonly_fields
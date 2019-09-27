from django.contrib import admin
from .models import Application, Income

# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('legal_agreement','signature',)
        return self.readonly_fields

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('application',)
        return self.readonly_fields
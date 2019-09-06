from django.contrib import admin
from .models import Application, Documents, Account

# Register your models here.
admin.site.register(Application)
admin.site.register(Documents)
admin.site.register(Account)
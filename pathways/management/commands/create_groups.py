# backend/management/commands/initgroups.py
from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission, User

from pathways.models import Application, Document

GROUPS_PERMISSIONS = {
    'Assister': {
        Application: ['add'],
        Document: ['add'],
    },
    'AuthenticationAdmin': {
        User: ['add','change','view'],
    },
    'StaffAdmin': {
        Application: ['add', 'change', 'view'],
        'historicalapplication': ['view'],
        Document: ['add', 'view'],
        'historicaldocument': ['view'],
    }
}

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)
            del created # unused

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in \
                        enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):
                    del perm_index # unused

                    # Generate permission name as Django would generate it
                    # Check if model is a str (for django-simple-history)
                    if isinstance(model_cls, str):
                        codename = perm_name + "_" + model_cls
                    else:
                        codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write("Adding "
                                          + codename
                                          + " to group "
                                          + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Define groups
        groups = ["Admin", "Respondent"]

        # Create or get groups
        for group in groups:
            group, created = Group.objects.get_or_create(name=group)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Group '{group}' created successfully"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Group '{group}' already exists"))

        # Grant admin group all permissions
        admin_group = Group.objects.filter(name="Admin").first()
        if admin_group:
            # Grant admin group all permissions
            permissions = Permission.objects.all()
            admin_group.permissions.add(*permissions)
            self.stdout.write(self.style.SUCCESS(f"Admin group has been granted all permissions'"))
            # Add admin to admin group
            user = get_user_model()
            admin = user.objects.filter(is_superuser=True).first()
            if admin:
                admin.groups.add(admin_group)
                self.stdout.write(self.style.SUCCESS(f"Admin '{admin}' has been granted all permissions'"))
            else:
                self.stdout.write(self.style.WARNING(f"No admin was found"))
        else:
            self.stdout.write(self.style.WARNING(f"No admin group was found"))

        # Grant necessary permissions to respondent group
        respondent_group = Group.objects.filter(name="Respondent").first()
        if respondent_group:
            content_types = [
                {"app_label": "surveys", "model": "surveyresponse", "action": "add"},
                {"app_label": "surveys", "model": "questionanswer", "action": "add"},
                {"app_label": "surveys", "model": "survey", "action": "view"},
                {"app_label": "surveys", "model": "section", "action": "view"},
                {"app_label": "surveys", "model": "question", "action": "view"},
                {"app_label": "surveys", "model": "questionchoice", "action": "view"},
                {"app_label": "surveys", "model": "surveyresponse", "action": "view"},
                {"app_label": "surveys", "model": "questionanswer", "action": "view"},
            ]

            for content_type in content_types:
                content_type_object = ContentType.objects.filter(
                    app_label=content_type["app_label"], model=content_type["model"]).first()

                if content_type_object:
                    permission = Permission.objects.filter(
                        content_type=content_type_object, codename__startswith=content_type["action"]).first()

                    if permission:
                        respondent_group.permissions.add(permission)
                        self.stdout.write(self.style.SUCCESS(f"Respondent group has been granted permission: {permission.name}"))

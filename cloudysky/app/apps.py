from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        # Import here to avoid circular import issues
        from django.core.management import call_command
        post_migrate.connect(seed_data, sender=self)

def seed_data(sender, **kwargs):
    # Run our seed command after migrations are applied
    try:
        from django.core.management import call_command
        call_command('seed_testdata')
    except Exception as e:
        print(f"Error seeding test data: {e}")
        # Don't raise the exception - we don't want to interrupt app startup

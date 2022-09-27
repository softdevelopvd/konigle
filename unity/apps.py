from django.apps import AppConfig


class UnityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unity'

class MyAppConfig(AppConfig):

    def ready(self):
        # Import celery app now that Django is mostly ready.
        # This initializes Celery and autodiscovers tasks
        import konigle.celery
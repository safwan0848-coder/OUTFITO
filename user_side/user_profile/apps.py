from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_side.user_profile"

    def ready(self):
        import user_side.user_profile.signals
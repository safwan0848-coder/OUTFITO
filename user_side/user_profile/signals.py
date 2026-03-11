from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_updated
from .models import Profile


@receiver(social_account_updated)
def save_google_avatar(request, sociallogin, **kwargs):

    user = sociallogin.user

    profile, created = Profile.objects.get_or_create(user=user)

    data = sociallogin.account.extra_data

    picture = data.get("picture")

    if picture:
        profile.google_image = picture
        profile.save()
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from user_side.authentication.models import OTP
from django.conf import settings
User = get_user_model()
from django.utils import timezone
import re
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.views.decorators.cache import never_cache


@never_cache
@login_required(login_url='login')
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        "user": request.user,
        "profile": profile
    }

    return render(request, "user/profile.html", context)


@never_cache
@login_required(login_url='login')
def edit_profile(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)


    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if not username or not email:
            messages.error(request, "Username and Email required")
            return redirect("edit-profile")

        elif not re.match(r'^[A-Za-z]+$', username):
            messages.error(request, "Username can contain only letters")
            return redirect("edit-profile")
        
        elif User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "user name already exists")
            return redirect("edit-profile")

        elif phone and not re.match(r'^[0-9]{10}$', phone):
            messages.error(request, "Phone must be 10 digits")
            return redirect("edit-profile")
      

        elif profile.google_image and email != request.user.email:
            messages.error(request, "Google users cannot change email address.")
            return redirect("profile")

        else:

            if email != request.user.email:

                request.session["new_email"] = email

                OTP.objects.filter(user=request.user).delete()
                otp = OTP.objects.create(user=request.user)

                send_mail(
                    subject="Verify Email Change",
                    message=f"Your OTP is {otp.code}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False
                )

                return redirect("verify-email-change")

            request.user.username = username
            request.user.save()

            profile.phone = phone

            if request.FILES.get("profile_image"):
                profile.profile_image = request.FILES.get("profile_image")

            profile.save()

            messages.success(request, "Profile updated successfully")

            return redirect("profile")

    context = {
        "user": request.user,
        "profile": profile,
    }

    return render(request, "user/edit_profile.html", context)


@never_cache
def logout_view(request):
   logout(request)
   return redirect('landing')

@never_cache
@login_required(login_url='login')
def address(request):
    return HttpResponse('address')
@never_cache
@login_required(login_url='login')
def wallet(request):
    return HttpResponse('wallet')
@never_cache
@login_required(login_url='login')
def orders(request):
    return HttpResponse('orders')
@never_cache
@login_required(login_url='login')
def wishlist(request):
    return HttpResponse('wishlist')


@never_cache
@login_required(login_url='login')
def change_password(request):

    profile = get_object_or_404(Profile, user=request.user)

    if profile.google_image:
        messages.error(request, "Password cannot be changed for Google accounts.")
        return redirect("profile")

    if request.method == "POST":

        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        user = request.user

        if not old_password or not new_password1 or not new_password2:
            messages.error(request, "All fields are required")
            return redirect("change-password")

        if not check_password(old_password, user.password):
            messages.error(request, "Current password is incorrect")
            return redirect("change-password")

        if len(new_password1) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("change-password")

        if new_password1 != new_password2:
            messages.error(request, "Passwords do not match")
            return redirect("change-password")

        if check_password(new_password1, user.password):
            messages.error(request, "New password cannot be the same as old password")
            return redirect("change-password")

        if not re.match(r'^[A-Za-z0-9@#$%^&+=!]+$', new_password1):
            messages.error(request, "Password contains invalid characters")
            return redirect("change-password")

        user.set_password(new_password1)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully")
        return redirect("profile")

    return render(request, "user/change_password.html")


def get_otp_timer(user):

    otp = OTP.objects.filter(user=user).last()

    remaining_seconds = 0

    if otp:
        remaining_seconds = int((otp.expired_at - timezone.now()).total_seconds())

        if remaining_seconds < 0:
            remaining_seconds = 0

    return otp, remaining_seconds


@never_cache
@login_required(login_url='login')
def start_password_reset(request):

    user = request.user

    otp, remaining_seconds = get_otp_timer(user)

    if otp and remaining_seconds > 0:
        messages.error(request, f"Please wait {remaining_seconds}s before requesting a new OTP.")
        return redirect("profile-reset-verify")

    OTP.objects.filter(user=user).delete()

    otp = OTP.objects.create(user=user)

    send_mail(
        subject="OTP Verification",
        message=f"Your OTP is {otp.code}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")

    return redirect("profile-reset-verify")


@never_cache
@login_required(login_url='login')
def profile_reset_verify(request):

    email = request.user.email

    user = get_object_or_404(User, email=email)

    otp = OTP.objects.filter(user=user).last()

    remaining_seconds = 0
    if otp:
        remaining_seconds = int((otp.expired_at - timezone.now()).total_seconds())
        if remaining_seconds < 0:
            remaining_seconds = 0

    if request.method == "POST":

        code = request.POST.get("otp")

        if not otp:
            messages.error(request, "OTP not found. Please request a new one.")
            return redirect('profile-reset-verify')

        if otp.is_expired():
            otp.delete()
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('profile-reset-verify')

        if str(otp.code) != str(code):
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('profile-reset-verify')

        otp.delete()

        request.session['otp_verified'] = True
        request.session.modified = True

        return redirect('profile-set-new-password')

    return render(request, 'user/profile_reset_verify.html', {
        "email": email,
        "remaining_seconds": remaining_seconds
    })


@never_cache
@login_required(login_url='login')
def profile_set_new_password(request):

    email = request.session.get('reset_email')
    verified = request.session.get('otp_verified')

    if not email or not verified:
        messages.error(request, "Unauthorized access. Please verify OTP first.")
        return redirect('change-password')

    if request.method == "POST":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            messages.error(request, "Password fields cannot be empty.")
            return redirect('profile-set-new-password')

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('profile-set-new-password')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('profile-set-new-password')

        if not re.match(r'^[A-Za-z0-9@#$%^&+=!]+$', password1):
            messages.error(request, "Password contains invalid characters.")
            return redirect('profile-set-new-password')

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "User not found.")
            return redirect('change-password')

        if check_password(password1, user.password):
            messages.error(request, "New password cannot be the same as the old password.")
            return redirect('profile-set-new-password')

        user.set_password(password1)
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        request.session.pop('reset_email', None)
        request.session.pop('otp_verified', None)

        messages.success(request, "Password reset successful!")

        return redirect('profile')

    return render(request, "user/profile_set_new_password.html")


@never_cache
@login_required(login_url='login')
def resend_profile_otp(request):

    new_email = request.session.get("new_email")

    if not new_email:
        messages.error(request, "Session expired. Please try again.")
        return redirect("profile")

    user = request.user

    otp, remaining_seconds = get_otp_timer(user)

    if otp and remaining_seconds > 0:
        messages.error(request, f"Please wait {remaining_seconds}s before requesting a new OTP.")
        return redirect("verify-email-change")

    OTP.objects.filter(user=user).delete()

    otp = OTP.objects.create(user=user)

    send_mail(
        subject="Email Change OTP",
        message=f"Your OTP is {otp.code}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[new_email],
        fail_silently=False
    )

    messages.success(request, "New OTP sent successfully")

    return redirect("verify-email-change")


@never_cache
@login_required(login_url='login')
@login_required
def verify_email_change(request):

    new_email = request.session.get("new_email")

    if not new_email:
        messages.error(request, "Session expired. Please try again.")
        return redirect("profile")

    if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
        messages.error(request, "This email is already in use.")
        request.session.pop("new_email", None)
        return redirect("edit-profile")

    user = request.user

    otp, remaining_seconds = get_otp_timer(user)

    if request.method == "POST":

        code = request.POST.get("otp")

        if not otp:
            messages.error(request, "OTP not found")
            return redirect("verify-email-change")

        if otp.is_expired():
            otp.delete()
            messages.error(request, "OTP expired. Please resend OTP.")
            return redirect("verify-email-change")

        if str(otp.code) != str(code):
            messages.error(request, "Invalid OTP")
            return redirect("verify-email-change")

        user.email = new_email
        user.save()

        otp.delete()
        request.session.pop("new_email", None)

        messages.success(request, "Email updated successfully")

        return redirect("profile")

    return render(request, "user/verify_email_change.html", {
        "email": new_email,
        "remaining_seconds": remaining_seconds
    })
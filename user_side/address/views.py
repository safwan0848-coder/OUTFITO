from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Address
from django.contrib import messages
import re
from django.views.decorators.cache import never_cache


@never_cache
@login_required(login_url='login')
def address_list(request):

    addresses = Address.objects.filter(user=request.user)

    return render(request, "user/address.html", {
        "addresses": addresses
    })



@never_cache
@login_required(login_url='login')
def add_address(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        line1 = request.POST.get("line1")
        line2 = request.POST.get("line2") or ""
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")
        country = request.POST.get("country")
        address_type = request.POST.get("type")
        is_default = request.POST.get("is_default")

        if not full_name:
            messages.error(request, "Full name is required")
            return redirect("add-address")

        if not re.match(r'^[A-Za-z ]+$', full_name):
            messages.error(request, "Full name can contain only letters")
            return redirect("add-address")

        if not phone:
            messages.error(request, "Phone number is required")
            return redirect("add-address")

        if not re.match(r'^[0-9]{10}$', phone):
            messages.error(request, "Phone number must be 10 digits")
            return redirect("add-address")

        if not line1:
            messages.error(request, "Address line 1 is required")
            return redirect("add-address")

        if not city:
            messages.error(request, "City is required")
            return redirect("add-address")

        if not re.match(r'^[A-Za-z ]+$', city):
            messages.error(request, "City can contain only letters")
            return redirect("add-address")

        if not state:
            messages.error(request, "State is required")
            return redirect("add-address")

        if not re.match(r'^[A-Za-z ]+$', state):
            messages.error(request, "State can contain only letters")
            return redirect("add-address")

        if not pincode:
            messages.error(request, "Pincode is required")
            return redirect("add-address")

        if not re.match(r'^[0-9]{6}$', pincode):
            messages.error(request, "Pincode must be 6 digits")
            return redirect("add-address")

        if not country:
            messages.error(request, "Country is required")
            return redirect("add-address")

        if not re.match(r'^[A-Za-z ]+$', country):
            messages.error(request, "Country can contain only letters")
            return redirect("add-address")

        if not address_type:
            messages.error(request, "Address type is required")
            return redirect("add-address")

        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone,
            address_line1=line1,
            address_line2=line2,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            type=address_type,
            is_default=True if is_default else False
        )

        messages.success(request, "Address added successfully")

        return redirect("address-list")

    return render(request, "user/add_address.html")


@never_cache
@login_required(login_url='login')
def edit_address(request, id):

    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":

        address.full_name = request.POST.get("full_name")
        address.phone_number = request.POST.get("phone")
        address.address_line1 = request.POST.get("line1")
        address.address_line2 = request.POST.get("line2") or ""
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.country = request.POST.get("country")
        address.type = request.POST.get("type")

        is_default = request.POST.get("is_default")

        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
        else:
            address.is_default = False

        address.save()

        return redirect("address-list")

    return render(request, "user/edit_address.html", {"address": address})

@login_required
def set_default_address(request, id):

    address = get_object_or_404(Address, id=id, user=request.user)

    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

    address.is_default = True
    address.save()

    return redirect("address-list")


@login_required
def delete_address(request, id):

    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully")
        return redirect("address-list")

    return redirect("address-list")
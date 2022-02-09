from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from accounts.forms import RegistrationForm
from .forms import RegistrationForm
from .models import Account
from cart.models import Cart, CartItem
from cart.views import _cart_id

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, "Check your inbox, you should have received a link to validate your account.")
            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                # If user added items to cart before logging in, they'll be
                # assigned to them
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You have successfully logged out. See you soon!")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # Setting user to active if the verification link is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "You have successfully activated your account!")
        return redirect("login")
    # Returning to registration page if the verification link is invalid
    else:
        messages.error(request, "Error: Invalid activation link.")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(
                email__exact=email
            )  # exact = case sensitive, iexact = case insensitive
            # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = "Reset your Password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request,
                "Check your inbox! We have sent you a link to reset your password.",
            )
            return redirect("login")
        else:
            messages.error(
                request, "An account linked to this email address doesn't exist."
            )
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please enter your new password below:")
        return redirect("resetPassword")
    else:
        messages.error(request, "Error: This link has expired.")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]
        # checking if passwords match
        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully!")
            return redirect("login")
        else:
            messages.error(request, "Error: Passwords do not match!")
            return redirect("resetPassword")
    # if method is not post, reload template
    else:
        return render(request, "accounts/resetPassword.html")

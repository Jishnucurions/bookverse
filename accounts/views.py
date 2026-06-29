from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random

from .forms import UserSignUpForm, UserUpdateForm, ProfileUpdateForm
from .models import OTPVerification
from books.models import SavedBook

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate user until OTP verified
            user.save()
            
            # Generate 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            OTPVerification.objects.update_or_create(user=user, defaults={'otp': otp_code})
            
            # Try to send email, print to console if fails
            try:
                send_mail(
                    subject="Bookverse - Verification Code",
                    message=f"Hello {user.username},\n\nYour 6-digit verification code is: {otp_code}\n\nThis code will expire in 10 minutes.",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                messages.info(request, "A verification code has been sent to your email address.")
            except Exception as e:
                # Console fallback so user can see it in terminal if credentials not set
                print(f"\n=========================================\n[OTP Fallback] Code for {user.username} is: {otp_code}\n=========================================\n")
                messages.warning(request, "We created your account but couldn't send the email. (Check server logs for code!)")
                
            return redirect('verify_otp', username=user.username)
    else:
        form = UserSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_otp_view(request, username):
    user = get_object_or_404(User, username=username)
    if user.is_active:
        messages.info(request, "This account is already verified.")
        return redirect('signin')
        
    if request.method == 'POST':
        typed_otp = request.POST.get('otp', '').strip()
        otp_record = getattr(user, 'otp_verification', None)
        
        if otp_record and otp_record.otp == typed_otp:
            if otp_record.is_expired():
                messages.error(request, "This verification code has expired. Please sign up again.")
                return render(request, 'accounts/verify_otp.html', {'user': user, 'error': 'Code expired'})
            
            # Success
            user.is_active = True
            user.save()
            otp_record.delete() # clean up
            messages.success(request, f"Account for {user.username} has been verified successfully! You can now log in.")
            return redirect('signin')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
            
    return render(request, 'accounts/verify_otp.html', {'user': user})

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})

def signout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('signin')

@login_required
def profile_settings_view(request):
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    p_change_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, "Your profile has been updated!")
                return redirect('profile_settings')
            else:
                messages.error(request, "Please correct the profile update errors.")
        elif action == 'change_password':
            p_change_form = PasswordChangeForm(request.user, request.POST)
            if p_change_form.is_valid():
                user = p_change_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated!")
                return redirect('profile_settings')
            else:
                messages.error(request, "Please correct the password change errors.")

    saved_books = SavedBook.objects.filter(user=request.user).order_by('-date_added')
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'p_change_form': p_change_form,
        'saved_books': saved_books
    }
    return render(request, 'accounts/profile_settings.html', context)

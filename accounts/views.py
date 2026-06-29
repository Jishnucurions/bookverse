from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import UserSignUpForm, UserUpdateForm, ProfileUpdateForm
from books.models import SavedBook

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}! You can now log in.")
            return redirect('signin')
    else:
        form = UserSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

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

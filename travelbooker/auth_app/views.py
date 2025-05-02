from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, ProfileUpdateForm

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember', False)
            
            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'auth/login.html', {'form': form})
            
            # Authenticate with username (since Django uses username as login)
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember me
                if not remember:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                # Redirect to next page if provided, otherwise to homepage
                next_url = request.GET.get('next', 'main:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def register(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists.')
                return render(request, 'auth/register.html', {'form': form})
            
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists.')
                return render(request, 'auth/register.html', {'form': form})
            
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to TravelBooker.')
            return redirect('main:index')
    else:
        form = RegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main:index')

@login_required
def profile(request):
    """User profile view and update"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        
        # Handle password change separately
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if form.is_valid():
            # Update profile information
            form.save()
            
            # Check if password change is requested
            if current_password and new_password and confirm_password:
                if not request.user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif new_password != confirm_password:
                    messages.error(request, 'New passwords do not match.')
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    # Update session to prevent logout
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Your password was successfully updated!')
            else:
                messages.success(request, 'Your profile was successfully updated!')
                
            return redirect('auth:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'auth/profile.html', {'form': form})

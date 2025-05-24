from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm # Import the UserCreationForm for signup view
from django.contrib.auth.decorators import login_required # Import the login_required decorator to protect views

# Create your views here.

def login_view(request):
    """Login view for the application."""
    
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to the dashboard if already logged in
    
    # Handle the login form submission
    if request.method == 'POST':
        username = request.POST['username'] 
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def signup_view(request):
    """Signup view for the application."""
    # Check if the user is already authenticated 
       
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to the dashboard if already logged in
    
    # Handle the signup form submission
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not password1 or not password2:
            messages.error(request, 'Toate câmpurile sunt obligatorii.')
            return render(request, 'accounts/signup.html', {'form': form})

        if form.is_valid():
            form.save()
            messages.success(request, 'Cont creat cu succes! Te poți loga.')
            return redirect('login')
        else:
            messages.error(request, 'Eroare la creare cont. Verifică datele introduse.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def dashboard_view(request):
    """Dashboard view for the application."""
    # Check if the user is authenticated        
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to the login page if not authenticated
    # Handle the dashboard view 
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    """Logout view for the application."""
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to the login page if not authenticated
    logout(request)
    return redirect('login')



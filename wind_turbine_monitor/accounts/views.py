from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm # Import the UserCreationForm for signup view
from django.contrib.auth.decorators import login_required # Import the login_required decorator to protect views

import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

logger = logging.getLogger(__name__)

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

@login_required
def energy_dashboard_view(request):
    """
    Render the energy dashboard page
    """
    return render(request, 'accounts/energy_dashboard.html')

@login_required
def energy_data_api(request):
    """
    Fetch energy data from ElectricityMap API and return it as JSON
    """
    try:
        response = requests.get(
            "https://api.electricitymap.org/v3/power-breakdown/latest?zone=RO",
            headers={
                "auth-token": "OkrQ5HqfIcLliXudfsjQ"  # Replace with your actual API key
            },
            timeout=10  # Add timeout to prevent hanging
        )
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)
        else:
            logger.error(f"ElectricityMap API error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': f'API returned status code {response.status_code}'
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to ElectricityMap API failed: {str(e)}")
        return JsonResponse({
            'error': f'Failed to fetch energy data: {str(e)}'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in energy_data_api: {str(e)}")
        return JsonResponse({
            'error': 'An unexpected error occurred'
        }, status=500)

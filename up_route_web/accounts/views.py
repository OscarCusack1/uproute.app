
import requests

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings

from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomPasswordChangeForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('address_view')  # Redirect to home page if user is already logged in
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('address_view')  # Redirect to a success page.
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout.

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('address_view')  # Redirect to a success page.
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

def api_key_view(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    api_key = user.api_key

    return render(request, 'api_keys.html', {'api_key': api_key})


def request_api_key(request):
    if request.method == 'POST':
        print("Requesting API key")
        user = request.user
        print(user)
        data = {'email': user.email}
        url = settings.UP_ROUTE_API_URL
        print(url)
        response = requests.post(f"{url}api/create_routes_api_key", json=data)
        print(response)
        if response.status_code == 200:
            response = response.json()
            print(user.api_key)
        else:
            print(response.json())
            return JsonResponse(response.json(), status=response.status_code)
        return JsonResponse({'message': 'request sent'})
    return redirect('api_key_view')
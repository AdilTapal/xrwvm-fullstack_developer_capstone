# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST method required"}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({"status": "error", "message": "Username and password are required"}, status=400)
        
        # Try to check if provided credentials can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({"status": "error", "message": "An error occurred during login"}, status=500)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_request(request):
    logout(request) # Terminate user session
    data = {"userName":""} # Return empty username
    return JsonResponse(data)



# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST method required"}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('userName', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not username or not email or not password:
            return JsonResponse({
                "status": "error", 
                "message": "Username, email, and password are required"
            }, status=400)
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[-1]:
            return JsonResponse({
                "status": "error",
                "message": "Invalid email format"
            }, status=400)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "userName": username,
                "status": "User already exists"
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "Email already registered"
            }, status=400)
        
        # Create user in auth_user table
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Login the user
        login(request, user)
        logger.debug(f"User {username} registered successfully")
        
        return JsonResponse({
            "userName": username,
            "status": "User Registered"
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({"status": "error", "message": "An error occurred during registration"}, status=500)


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...

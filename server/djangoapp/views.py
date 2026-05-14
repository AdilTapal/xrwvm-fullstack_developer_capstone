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
import requests
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .restapis import backend_url


# Get an instance of a logger
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CAR_RECORDS_FILE = BASE_DIR / 'database' / 'data' / 'car_records.json'


def _backend_get(endpoint):
    response = requests.get(f"{backend_url}{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


def _backend_post(endpoint, payload):
    response = requests.post(
        f"{backend_url}{endpoint}",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


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
def get_dealerships(request, state=None):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "GET method required"}, status=405)
    try:
        state = state or request.GET.get('state')
        if state and state != 'All':
            dealerships = _backend_get(f"/fetchDealers/{state}")
        else:
            dealerships = _backend_get("/fetchDealers")

        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error(f"Error fetching dealerships: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching dealerships"}, status=500)

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "GET method required"}, status=405)
    try:
        reviews = _backend_get(f"/fetchReviews/dealer/{dealer_id}")
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as e:
        logger.error(f"Error fetching dealer reviews: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching dealer reviews"}, status=500)

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "GET method required"}, status=405)
    try:
        dealer = _backend_get(f"/fetchDealer/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": dealer})
    except Exception as e:
        logger.error(f"Error fetching dealer details: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching dealer details"}, status=500)

# Create a `add_review` view to submit a review
def add_review(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST method required"}, status=405)
    try:
        payload = json.loads(request.body)
        result = _backend_post("/insert_review", payload)
        return JsonResponse({"status": 200, "review": result})
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error adding review"}, status=500)


def get_cars(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "GET method required"}, status=405)
    try:
        with open(CAR_RECORDS_FILE, 'r', encoding='utf-8') as file_handle:
            car_records = json.load(file_handle).get('cars', [])

        unique_cars = []
        seen = set()
        for car in car_records:
            key = (car.get('make'), car.get('model'))
            if key in seen:
                continue
            seen.add(key)
            unique_cars.append({
                'CarMake': car.get('make'),
                'CarModel': car.get('model'),
            })

        return JsonResponse({"status": 200, "CarModels": unique_cars})
    except Exception as e:
        logger.error(f"Error fetching cars: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching cars"}, status=500)
# def get_cars(request):
#     count = CarMake.objects.filter().count()
#     print(count)
#     if(count == 0):
#         initiate()
#     car_models = CarModel.objects.select_related('car_make')
#     cars = []
#     for car_model in car_models:
#         cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
#     return JsonResponse({"CarModels":cars})

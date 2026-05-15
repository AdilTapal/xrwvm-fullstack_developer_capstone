# Uncomment the required imports before adding the code

from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import logging
import json
import requests
from pathlib import Path

from .restapis import backend_url
# from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CAR_RECORDS_FILE = BASE_DIR / "database" / "data" / "car_records.json"


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
    if request.method != "POST":
        msg = "POST method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")

        if not username or not password:
            msg = "Username and password are required"
            return JsonResponse(
                {"status": "error", "message": msg}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse(
                {"userName": username, "status": "Authenticated"})
        else:
            msg = "Invalid credentials"
            return JsonResponse(
                {"status": "error", "message": msg}, status=401)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        msg = "An error occurred during login"
        return JsonResponse({"status": "error", "message": msg}, status=500)


@csrf_exempt
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    if request.method != "POST":
        msg = "POST method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not username or not email or not password:
            msg = "Username, email, and password are required"
            return JsonResponse(
                {"status": "error", "message": msg}, status=400)

        if "@" not in email or "." not in email.split("@")[-1]:
            msg = "Invalid email format"
            return JsonResponse(
                {"status": "error", "message": msg}, status=400)

        if User.objects.filter(username=username).exists():
            msg = "User already exists"
            return JsonResponse(
                {"userName": username, "status": msg}, status=400)

        if User.objects.filter(email=email).exists():
            msg = "Email already registered"
            return JsonResponse(
                {"status": "error", "message": msg}, status=400)

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()

        login(request, user)
        logger.debug(f"User {username} registered successfully")

        return JsonResponse(
            {"userName": username, "status": "User Registered"},
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        msg = "An error occurred during registration"
        return JsonResponse({"status": "error", "message": msg}, status=500)


def get_dealerships(request, state="All"):
    if request.method != "GET":
        msg = "GET method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)
    try:
        state = state or request.GET.get("state")
        if state and state != "All":
            dealerships = _backend_get(f"/fetchDealers/{state}")
        else:
            dealerships = _backend_get("/fetchDealers")

        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error(f"Error fetching dealerships: {str(e)}")
        msg = "Error fetching dealerships"
        return JsonResponse({"status": 500, "message": msg}, status=500)


def get_dealer_reviews(request, dealer_id):
    if request.method != "GET":
        msg = "GET method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)
    try:
        reviews = _backend_get(f"/fetchReviews/dealer/{dealer_id}")
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as e:
        logger.error(f"Error fetching dealer reviews: {str(e)}")
        msg = "Error fetching dealer reviews"
        return JsonResponse({"status": 500, "message": msg}, status=500)


def get_dealer_details(request, dealer_id):
    if request.method != "GET":
        msg = "GET method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)
    try:
        dealer = _backend_get(f"/fetchDealer/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": dealer})
    except Exception as e:
        logger.error(f"Error fetching dealer details: {str(e)}")
        msg = "Error fetching dealer details"
        return JsonResponse({"status": 500, "message": msg}, status=500)


@csrf_exempt
def post_review(request):
    if request.method != "POST":
        msg = "POST method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)
    try:
        payload = json.loads(request.body)
        result = _backend_post("/insert_review", payload)
        return JsonResponse({"status": 200, "review": result})
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": 400, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        return JsonResponse(
            {"status": 500, "message": "Error adding review"}, status=500
        )


def get_cars(request):
    if request.method != "GET":
        msg = "GET method required"
        return JsonResponse({"status": "error", "message": msg}, status=405)
    try:
        with open(CAR_RECORDS_FILE, "r", encoding="utf-8") as file_handle:
            car_records = json.load(file_handle).get("cars", [])

        unique_cars = []
        seen = set()
        for car in car_records:
            key = (car.get("make"), car.get("model"))
            if key in seen:
                continue
            seen.add(key)
            unique_cars.append(
                {
                    "CarMake": car.get("make"),
                    "CarModel": car.get("model"),
                }
            )

        return JsonResponse({"status": 200, "CarModels": unique_cars})
    except Exception as e:
        logger.error(f"Error fetching cars: {str(e)}")
        return JsonResponse(
            {"status": 500, "message": "Error fetching cars"}, status=500
        )

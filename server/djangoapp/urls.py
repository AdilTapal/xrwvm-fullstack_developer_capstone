from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "djangoapp"
urlpatterns = [
    path(route="login", view=views.login_user, name="login"),
    path(route="logout", view=views.logout_request, name="logout"),
    path(route="register", view=views.registration, name="register"),
    path(route="dealers", view=views.get_dealerships, name="dealers"),
    path(route="get_dealers", view=views.get_dealerships, name="get_dealers"),
    path(
        route="get_dealers/<str:state>",
        view=views.get_dealerships,
        name="get_dealers_by_state",
    ),
    path(
        route="dealer/<int:dealer_id>",
        view=views.get_dealer_details,
        name="dealer_details",
    ),
    path(
        route="reviews/dealer/<int:dealer_id>",
        view=views.get_dealer_reviews,
        name="dealer_reviews_by_dealer",
    ),
    path(route="get_cars", view=views.get_cars, name="get_cars"),
    path(
        route="dealer-reviews",
        view=views.get_dealer_reviews,
        name="dealer_reviews"),
    path(route="post-review", view=views.post_review, name="post_review"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path

from . import views  # Import your views here

urlpatterns = [
    path("employees/", views.CreateEmployeeView.as_view(), name="employee-create"),
    path(
        "restaurants/", views.CreateRestaurantView.as_view(), name="restaurant-create"
    ),
    path("menu/", views.UploadMenuView.as_view(), name="menu-create"),
    path("menu/today/", views.TodayMenuView.as_view(), name="menu-today"),
    path("vote/", views.VoteView.as_view(), name="vote"),
    path("results/today/", views.TodayResultsView.as_view(), name="results-today"),
]

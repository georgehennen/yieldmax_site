from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name="dashboard"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("api/get_portfolio_data/", views.get_portfolio_data_api, name="get_portfolio_data"),
]
from django.urls import path
from . import views

app_name = 'screener'

urlpatterns = [
    path('', views.screener_view, name='index'), 
    # New URL for our background data fetching
    path('api/get-screener-data/', views.get_screener_data_api, name='get_screener_data'),
]
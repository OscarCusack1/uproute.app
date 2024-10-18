from django.urls import path
from .views import login_view, logout_view, register_view, change_password, api_key_view, request_api_key

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('change-password/', change_password, name='change_password'),
    path('api-keys/', api_key_view, name='api_key_view'),
    path('api-keys-request/', request_api_key, name='request_api_key'),
]
from django.urls import path
from user import views

urlpatterns = [
    path('sms',views.sms_view)
]
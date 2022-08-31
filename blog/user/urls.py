from django.urls import path
from user import views

urlpatterns = [
    path('sms',views.sms_view),
    path('<str:username>',views.UserView.as_view()),
    path('<str:username>/avatar',views.avatar_view)
]
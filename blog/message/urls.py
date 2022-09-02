from django.urls import path

from message import views

urlpatterns = [
    path('<int:t_id>',views.message_view)
]
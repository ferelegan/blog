from django.urls import path
from topic import views

urlpatterns = [
    path('<str:author_id>',views.TopicView.as_view())
]
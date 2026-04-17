from django.urls import path
from .views import ProfileView
from . import views

urlpatterns = [
    path("api/profiles", ProfileView.as_view()),
    path("api/profiles/<uuid:id>", ProfileView.as_view()),

]


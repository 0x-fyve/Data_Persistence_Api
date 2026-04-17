from django.urls import path
from . import views

urlpatterns = [
    path('api/profiles', views.Post, name="Post", ),
    path('api/profiles/<str:id>', views.Get, name="Get"),
    path('api/profiles<str:id>', views.Delete, name="Delete"),

]


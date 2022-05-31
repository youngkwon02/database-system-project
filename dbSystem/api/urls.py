from . import views
from django.urls import path

urlpatterns = [
    path("select/", views.select),
    path("insert/", views.insert),
]

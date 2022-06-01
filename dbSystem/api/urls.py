from . import views
from django.urls import path

urlpatterns = [
    path("create/", views.create),
    path("select/", views.select),
    path("insert/", views.insert),
]

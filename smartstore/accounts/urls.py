from django.urls import path, include
from .views import registrazione_view

urlpatterns = [
    path('registrazione/', registrazione_view, name="registrazione_view")
]

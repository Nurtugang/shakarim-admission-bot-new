from django.urls import path
from .views import smart_ask_gemini

urlpatterns = [
    path("smart_ask_gemini/", smart_ask_gemini),
]

from django.urls import path
from .views import LoginView, VerifyView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('auth/', VerifyView.as_view()),
]


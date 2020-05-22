from django.urls import path
from .views import HomeView,AuthView,AuthCallbackView

urlpatterns = [
    path('', HomeView.as_view() , name='home'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('auth_callback/', AuthCallbackView.as_view() , name='auth_callback'),
]

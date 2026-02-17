from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


urlpatterns = [

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.OnBoardingView.as_view(), name='onboarding'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
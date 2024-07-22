from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path("register", views.RegisterAPIView.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('change-password', views.ChangePasswordAPIView.as_view()),

    path('services', views.CarServiceListView.as_view()),
    path('services/<pk>/details', views.CarServiceDetailsView.as_view()),
    path('services/<pk>/available/<date_from>/<date_to>', views.CarServiceAvailableScheduleView.as_view()),
    path('services/schedule', views.CarServiceSubmitScheduleView.as_view()),

    path("profile/submits", views.UserSubmitsView.as_view()),
]

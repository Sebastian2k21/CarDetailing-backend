from django.urls import path
from . import views
from . import views_detailer

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
    path('services/<pk>/days', views.CarServiceDaysView.as_view()),
    path('services/<pk>/available/<date_from>/<date_to>', views.CarServiceAvailableScheduleView.as_view()),
    path('services/schedule', views.CarServiceSubmitScheduleView.as_view()),

    path("profile/submits", views.UserSubmitsView.as_view()),
    path("profile/submits/<submit_id>/delete", views.DeleteSubmitScheduleView.as_view()),
    path("profile/submits/<submit_id>/change", views.UpdateSubmitScheduleView.as_view()),
    path("profile/details", views.UserProfileView.as_view()),
    path("profile/role", views.UserRoleView.as_view()),

    path("cars", views.CarsView.as_view()),
    path("cars/add", views.AddCarView.as_view()),
    path("cars/<car_id>/delete", views.RemoveCarView.as_view()),

    ## Detailer ----------------------------------------------------------------------------------------

    path("detailer/stats", views_detailer.DetailerStatsView.as_view()),

    path("detailer/services", views_detailer.DetailerServicesListView.as_view()),
    path("detailer/services/add", views_detailer.AddServiceView.as_view()),

    path("detailer/orders", views_detailer.OrdersListView.as_view()),
    path("detailer/orders/<order_id>/attach-employee", views_detailer.AttachEmployeeView.as_view()),
    path("detailer/orders/<order_id>/set-status", views_detailer.SetSubmitStatusView.as_view()),

    path("detailer/analytics/<date_from>/<date_to>", views_detailer.DetailerAnalyticsView.as_view()),

    path("detailer/clients", views_detailer.DetailerClientsView.as_view()),
    path("detailer/clients/<client_id>/submits", views_detailer.DetailerClientSubmitsView.as_view()),

    path("employees", views_detailer.EmployeesView.as_view()),
    path("employees/add", views_detailer.AddEmployeeView.as_view()),
    path("employees/<employee_id>/delete", views_detailer.RemoveEmployeeView.as_view()),

    path("status", views_detailer.SubmitStatusListView.as_view()),
]

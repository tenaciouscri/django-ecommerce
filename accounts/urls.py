from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),
    path(
        "activate/<uidb64>/<token>/", views.activate, name="activate"
    ),  # User activation
    path(
        "forgotPassword/", views.forgotPassword, name="forgotPassword"
    ),  # Forgot password
    path(
        "resetpassword_validate/<uidb64>/<token>/",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),  # Password reset landing page
    path(
        "resetPassword/", views.resetPassword, name="resetPassword"
    ),  # Password reset page
]

from django.urls import path
from users import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("validate", views.ValidateAccessTokenView.as_view(), name="validate-token"),
    path("refresh", views.RefreshAccessTokenView.as_view(), name="refresh-token"),
    path("me/tracker", views.UserMeTrackerView.as_view(), name="user-tracker"),
]

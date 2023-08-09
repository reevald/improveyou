from django.urls import path
from users import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("validate", views.ValidateAccessTokenView.as_view(), name="validate-token"),
    path("refresh", views.RefreshAccessTokenView.as_view(), name="refresh-token"),
    path("me/object", views.UserMeObjectView.as_view(), name="user-object"),
    path("me/gamestat", views.UserMeGameStatView.as_view(), name="user-gamestat"),
    path(
        "me/username",
        views.UserMeChangeUsernameView.as_view(),
        name="user-change-username",
    ),
    path(
        "me/publicity",
        views.UserMeChangePublicityView.as_view(),
        name="user-change-publicity",
    ),
    path("me/bag/items", views.UserMeBagItemView.as_view(), name="user-bag-item"),
    path(
        "me/bag/equipitem",
        views.UserMeBagEquipItemView.as_view(),
        name="user-bag-equip-item",
    ),
    path("me/dailycheck", views.UserMeDailyCheckView.as_view(), name="user-dailycheck"),
    path("me/tasks", views.UserMeTaskProgressView.as_view(), name="user-tasks"),
    path(
        "me/event-rewards",
        views.UserMeEventRewardView.as_view(),
        name="user-event-rewards",
    ),
    path("me/tracker", views.UserMeTrackerView.as_view(), name="user-tracker"),
]

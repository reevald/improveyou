from activities import views
from django.urls import path

urlpatterns = [
    path(
        "<str:category>/<slug:slug>",
        views.ActivityDetailView.as_view(),
        name="activity-detail",
    )
]

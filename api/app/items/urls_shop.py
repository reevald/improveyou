from django.urls import path
from items import views

urlpatterns = [
    path("items", views.ShopItemView.as_view(), name="shop-items"),
]

from django.urls import path
from items import views

urlpatterns = [
    path("items", views.ShopItemView.as_view(), name="shop-items"),
    path("buy/item", views.BuyItemView.as_view(), name="buy-item"),
]

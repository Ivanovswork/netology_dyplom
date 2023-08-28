from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet, CategoryViewSet, ProductView, RegistrUserView, login, logout, get_product_info, \
    confirm_email, UserContactView, BasketView, OrderView, confirm_order, ShopStatusView

r = DefaultRouter()
r.register('shop', ShopViewSet)
r.register('category', CategoryViewSet)

urlpatterns = [

    path("admin/", admin.site.urls),
    path("change_shop_status/", ShopStatusView.as_view()),
    path("product/", ProductView.as_view()),
    path("registration/", RegistrUserView.as_view()),
    path("login/", login),
    path("logout/", logout),
    path("prinf/<int:product_id>/", get_product_info,),
    path("confirm/<str:key>/", confirm_email),
    path("contact_info/", UserContactView.as_view()),
    path("basket/", BasketView.as_view()),
    path("order/", OrderView.as_view()),
    path("confirm_order/<str:key>/<str:id>/", confirm_order)

] + r.urls

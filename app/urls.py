from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet, CategoryViewSet, ProductView, RegistrUserView, login, logout

r = DefaultRouter()
r.register('shop', ShopViewSet)
r.register('category', CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("product/", ProductView.as_view()),
    path("registration/", RegistrUserView.as_view()),
    path("login/", login),
    path("logout/", logout)
] + r.urls

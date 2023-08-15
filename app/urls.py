from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet


r = DefaultRouter()
r.register('shop', ShopViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
] + r.urls

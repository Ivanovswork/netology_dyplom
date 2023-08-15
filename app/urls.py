from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet, CategoryViewSet, ProductView

r = DefaultRouter()
r.register('shop', ShopViewSet)
r.register('category', CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('product/', ProductView.as_view())
] + r.urls

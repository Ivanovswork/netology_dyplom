from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopSerializer, CategorySerializer
from .permissions import GetShop, IsStaff


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.filter(status=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, GetShop]


class CategoryViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsStaff]



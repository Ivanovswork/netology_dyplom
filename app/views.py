from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Shop
from .serializers import ShopSerializer
from .permissions import GetShop


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.filter(status=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, GetShop]



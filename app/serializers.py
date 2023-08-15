from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from .models import Shop, Category, Product


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'status',
        ]


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']

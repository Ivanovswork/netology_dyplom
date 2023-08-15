from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from .models import Shop, Category


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


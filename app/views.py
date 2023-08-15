import json

from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Shop, Product, Category, ProductInfo
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer
from .permissions import GetShop, IsSuperuser, IsStaff
import yaml


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.filter(status=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, GetShop]


class CategoryViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsSuperuser]


class ProductView(APIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    http_method_names = ['get', 'post']

    def get(self, request):
        queryset = Product.objects.all()
        s = ProductSerializer(queryset, many=True)
        return JsonResponse(data=s.data, safe=False)

    def post(self, request, *args, **kwargs):
        with open('./data/shop1.yaml', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            # print(data)

            shop = list(Shop.objects.filter(name=data['shop']))[0]

            for elem in data['categories']:
                print(elem)
                category = list(Category.objects.filter(id=elem['id']))[0]
                category.shop.add(shop)

            for elem in data['goods']:
                category = list(Category.objects.filter(id=int(elem['category'])))[0]
                p = Product(name=(elem['name'].encode('utf-8').decode()), category=category)
                p.save()
                pi = ProductInfo(
                    product=p,
                    shop=shop,
                    model=elem['model'],
                    price=elem['price'],
                    quantity=elem['quantity'],
                    params=json.dumps(elem['parameters'])
                )
                pi.save()

        return Response({'status': 'OK'})

import json

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Shop, Product, Category, ProductInfo, Param, User
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer, UserRGSTRSerializer, UserLoginSerializer
from .permissions import GetShop, IsSuperuser, IsStaff
from rest_framework.authtoken.models import Token
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
                p_i = ProductInfo(
                    product=p,
                    shop=shop,
                    model=elem['model'],
                    price=elem['price'],
                    quantity=elem['quantity'],
                )
                p_i.save()
                for name, value in elem['parameters'].items():
                    param = Param(name=name, value=value, product=p)
                    param.save()

        return Response({'status': 'OK'})


class RegistrUserView(APIView):
    queryset = User.objects.all()

    serializer_class = UserRGSTRSerializer

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRGSTRSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({'request': 'True'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)


@api_view(['POST'])
def login(request, *args, **kwargs):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'Ошибка': 'Ошибка входа в систему'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request, *args, **kwargs):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'Информация': 'Вы успешно вышли из системы.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Ошибка.': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Shop, Product, Category, ProductInfo, Param, User, ConfirmEmailKey, Contact, Order, OrderItem
from .serializers import ShopSerializer, CategorySerializer, ProductSerializer, UserRGSTRSerializer, \
    UserContactSerializer
from .permissions import GetShop, IsSuperuser, IsStaff
from .forms import ContactForm, OrderItemForm, OrderItemUpdateForm
from rest_framework.authtoken.models import Token
import yaml
from django.core.mail import send_mail


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
        user = UserRGSTRSerializer(data=request.data)

        if user.is_valid():
            user = user.save()
            key = ConfirmEmailKey(user=user)
            key.save()

            send_mail(
                "destira@mail.ru",
                f"http://127.0.0.1:8000/confirm/{key.key}/",
                EMAIL_HOST_USER,
                ["netology_dyplom@mail.ru"],
                fail_silently=False,
            )

            return Response({'Информация': 'Регистрация прошла успешно'}, status=status.HTTP_200_OK)
        return Response(user.errors)


@api_view()
def confirm_email(request, key, *args, **kwargs):
    try:
        user_key = ConfirmEmailKey.objects.filter(key=key).first()
        user = user_key.user
        user.is_active = True
        user.save()
        return Response({'Информация': 'Вы успешно подтвердили email'}, status=status.HTTP_200_OK)
    except:
        return Response({'Ошибка': 'Пользователь с таким ключем не найден'}, status=status.HTTP_404_NOT_FOUND)


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


@api_view(["GET"])
def get_product_info(request, product_id):
    try:
        product = list(Product.objects.filter(id=product_id))[0]
    except:
        return Response({'Ошибка': 'Данный товар не найден.'}, status=status.HTTP_404_NOT_FOUND)
    prinf = list(ProductInfo.objects.filter(product=product))[0]
    data = {
        "id": product.id,
        "name": product.name,
        "shop": prinf.shop.name,
        "model": prinf.model,
        "price": prinf.price,
        "quantity": prinf.quantity,
        "parameters": {}
    }
    params = list(Param.objects.filter(product=product))
    for param in params:
        data["parameters"][param.name] = param.value
    return Response(data)


class UserContactView(APIView):
    queryset = Contact.objects.all()
    serializer_class = UserContactSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        contact = Contact.objects.filter(user=user).first()
        if contact:
            return Response({
                "user_id": contact.user.id,
                "username": contact.user.email,
                "adress": contact.adress,
                "telephone_number": contact.t_number
            })
        else:
            return Response({"Информация": "Ваши контактные данные не указаны"})

    def post(self, request, *args, **kwargs):
        user = request.user
        contact = Contact.objects.filter(user=user)
        if contact:
            return Response({"Информация": "У вас уже имеется контактная информация"})
        else:
            data = request.data
            form = ContactForm(data)
            if form.is_valid():
                try:
                    contact = Contact(user=user, adress=data["adress"], t_number=data["t_number"])
                    contact.save()
                except:
                    return Response({"status": "Bad request"})
            else:
                return Response({"status": "Bad request"})

            return Response({"status": "OK"})

    def put(self, request, *args, **kwargs):
        user = request.user
        contact = Contact.objects.filter(user=user)
        print(contact.first().adress)
        if not contact:
            return Response({"Информация": "Изменять нечего"})
        else:
            data = request.data
            form = ContactForm(data)
            if form.is_valid():
                try:
                    contact.update(adress=data["adress"], t_number=data["t_number"])
                except:
                    return Response({"status": "Bad request"})
            else:
                return Response({"status": "Bad request"})

            return Response({"status": "OK"})

    def delete(self, request, *args, **kwargs):
        user = request.user
        contact = Contact.objects.filter(user=user)
        if not contact:
            return Response({"Информация": "У вас нет контактной информации"})
        else:
            try:
                contact.delete()
            except:
                return Response({"status": "Bad request"})
        return Response({"status": "OK"})


class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        basket = list(Order.objects.filter(user=user, state='basket'))[-1]
        if basket:
            orderitems = OrderItem.objects.filter(order=basket)
            response = {}
            for i, elem in enumerate(orderitems):
                response[i + 1] = {
                    "id": elem.product_info.product.id,
                    "name": elem.product_info.product.name,
                    "category": elem.product_info.product.category.name,
                    "shop": elem.product_info.shop.name,
                    "quantity": elem.quantity,
                    "model": elem.product_info.model,
                    "price": elem.product_info.price,
                }
            return Response(response)
        else:
            return Response({"status": "No Items"})

    def post(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user, state='basket')
        if orders:
            basket = list(orders)[-1]
        else:
            contact = list(Contact.objects.filter(user=user))[0]
            basket = Order(
                user=user,
                state="basket",
                contact=contact
            )
            basket.save()
        data = request.data
        form = OrderItemForm(data)

        if form.is_valid():
            productinfo = ProductInfo.objects.filter(id=data['product_info']).first()
            if OrderItem.objects.filter(order=basket, product_info=productinfo):
                return Response({"status": "Bad request", "Reason": "Product has already been in basket"})
            quantity = data['quantity']
            if quantity > productinfo.quantity:
                return Response({"status": "Bad request", "Reason": "Quantity"})
            orderitem = OrderItem(
                order=basket,
                product_info=productinfo,
                quantity=quantity
            )
            orderitem.save()
            return Response({"status": "OK"})
        else:
            return Response({"status": "Bad request"})

    def patch(self, request, *args, **kwargs):
        user = request.user
        basket = list(Order.objects.filter(user=user, state='basket'))[-1]
        if basket:
            data = request.data
            form = OrderItemUpdateForm(data)
            if form.is_valid():
                order_item = OrderItem.objects.filter(id=data['orderitem_id']).first()
                if not(order_item):
                    return Response({"status": "Bad request", "Reason": "bad order item id"})
                if order_item.order != basket:
                    return Response({"status": "Bad request", "Reason": "bad order item id"})
                quantity = data['quantity']
                if quantity > order_item.product_info.quantity:
                    return Response({"status": "Bad request", "Reason": "Quantity"})
                order_item.quantity = quantity
                order_item.save()
                return Response({"status": "OK"})
            else:
                return Response({"status": "Bad request"})
        else:
            return Response({"status": "No Items"})

    def delete(self, request, *args, **kwargs):
        user = request.user
        basket = list(Order.objects.filter(user=user, state='basket'))[-1]
        if basket:
            OrderItem.objects.filter(order=basket).delete()
            return Response({"status": "OK"})
        else:
            return Response({"status": "No Items"})
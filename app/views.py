from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import (
    Shop,
    Product,
    Category,
    ProductInfo,
    Param,
    User,
    ConfirmEmailKey,
    Contact,
    Order,
    OrderItem,
)
from .serializers import (
    ShopSerializer,
    CategorySerializer,
    ProductSerializer,
    UserRGSTRSerializer,
    UserContactSerializer,
)
from .permissions import GetShop, IsSuperuser, IsStaff
from .forms import ContactForm, OrderItemForm, OrderItemUpdateForm
from rest_framework.authtoken.models import Token
import yaml
from django.core.mail import send_mail


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.filter(status=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, GetShop]


class ShopStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.company_id:
            shop = Shop.objects.get(pk=user.company_id)
            if shop.status:
                shop.status = False
            else:
                shop.status = True
            shop.save()
            return Response({"status": "Status of shop has ben changed"})
        else:
            return Response({"status": "You are not staff"})


@api_view(["GET"])
def get_orders(request, *args, **kwargs):
    user = request.user
    if type(user) != AnonymousUser:
        if user.company_id:
            shop = Shop.objects.get(pk=user.company_id)
            orders = list(Order.objects.all())
            data = {}
            for order in orders:
                a = 0
                orderitems = list(OrderItem.objects.filter(order=order))
                if order.state != "basket" or order.state != "basket":
                    for orderitem in orderitems:
                        if orderitem.product_info.shop == shop:
                            if a == 0:
                                data[order.id] = []
                                a += 1
                            data[order.id].append(
                                {
                                    "orderitem_id": orderitem.id,
                                    "orderitem_state": order.state,
                                    "product_name": orderitem.product_info.product.name,
                                    "quantity": orderitem.quantity,
                                }
                            )
            return Response(data)
        else:
            return Response({"status": "You are not staff"})
    else:
        return Response({"status": "Anonymous"})


class CategoryViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsSuperuser]


class ProductView(APIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    http_method_names = ["get", "post"]

    def get(self, request):
        queryset = Product.objects.all()
        s = ProductSerializer(queryset, many=True)
        return JsonResponse(data=s.data, safe=False)

    def post(self, request, *args, **kwargs):
        with open("./data/shop1.yaml", encoding="utf-8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            # print(data)

            shop = list(Shop.objects.filter(name=data["shop"]))

            if shop:
                shop = shop[0]
                for elem in data["categories"]:
                    print(elem)
                    category = list(Category.objects.filter(id=elem["id"]))[0]
                    category.shop.add(shop)

                for elem in data["goods"]:
                    category = list(Category.objects.filter(id=int(elem["category"])))[
                        0
                    ]
                    p = Product(
                        name=(elem["name"].encode("utf-8").decode()), category=category
                    )
                    p.save()
                    p_i = ProductInfo(
                        product=p,
                        shop=shop,
                        model=elem["model"],
                        price=elem["price"],
                        quantity=elem["quantity"],
                    )
                    p_i.save()
                    for name, value in elem["parameters"].items():
                        param = Param(name=name, value=value, product=p)
                        param.save()

                return Response({"status": "OK"})
            else:
                return Response({"status": "Bad yaml file"})


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
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"status": "Registration has been done"}, status=status.HTTP_200_OK
            )
        return Response(user.errors)


@api_view()
def confirm_email(request, key, *args, **kwargs):
    user_key = ConfirmEmailKey.objects.filter(key=key).first()
    if user_key:
        user = user_key.user
        user.is_active = True
        user.save()
        return Response(
            {"status": "email has been comfirmed"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"status": "User with this key not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def login(request, *args, **kwargs):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")

        user = None
        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(
            {"Ошибка": "Ошибка входа в систему"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request, *args, **kwargs):
    if request.method == "POST":
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response(
                {"status": "Logout has been completed"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status.": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["GET"])
def get_product_info(request, product_id):
    try:
        product = list(Product.objects.filter(id=product_id))[0]
    except:
        return Response(
            {"status": "This product is not found"}, status=status.HTTP_404_NOT_FOUND
        )
    prinf = ProductInfo.objects.filter(product=product).first()
    data = {
        "id": product.id,
        "name": product.name,
        "shop": prinf.shop.name,
        "model": prinf.model,
        "price": prinf.price,
        "quantity": prinf.quantity,
        "parameters": {},
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
            return Response(
                {
                    "user_id": contact.user.id,
                    "username": contact.user.email,
                    "adress": contact.adress,
                    "telephone_number": contact.t_number,
                }
            )
        else:
            return Response({"status": "Your contact details are not specified"})

    def post(self, request, *args, **kwargs):
        user = request.user
        contact = Contact.objects.filter(user=user)
        if contact:
            return Response({"status": "Your contact details has been specified"})
        else:
            data = request.data
            form = ContactForm(data)
            if form.is_valid():
                try:
                    contact = Contact(
                        user=user, adress=data["adress"], t_number=data["t_number"]
                    )
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
            return Response({"status": "Your contact details are not specified"})
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
            return Response({"status": "Your contact details are not specified"})
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
        basket = list(Order.objects.filter(user=user, state="basket"))
        if basket:
            basket = basket[-1]
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
        orders = Order.objects.filter(user=user, state="basket")
        if orders:
            basket = list(orders)[-1]
        else:
            contact = list(Contact.objects.filter(user=user))[0]
            basket = Order(user=user, state="basket", contact=contact)
            basket.save()
        data = request.data
        form = OrderItemForm(data)

        if form.is_valid():
            productinfo = ProductInfo.objects.filter(id=data["product_info"]).first()
            if OrderItem.objects.filter(order=basket, product_info=productinfo):
                return Response(
                    {
                        "status": "Bad request",
                        "Reason": "Product has already been in basket",
                    }
                )
            quantity = data["quantity"]
            if quantity > productinfo.quantity:
                return Response({"status": "Bad request", "Reason": "Quantity"})
            if productinfo.shop.status:
                orderitem = OrderItem(
                    order=basket, product_info=productinfo, quantity=quantity
                )
                orderitem.save()
                return Response({"status": "OK"})
            else:
                return Response({"status": "Shop is not active"})
        else:
            return Response({"status": "Bad request"})

    def patch(self, request, *args, **kwargs):
        user = request.user
        basket = list(Order.objects.filter(user=user, state="basket"))
        if basket:
            basket = basket[-1]
            data = request.data
            form = OrderItemUpdateForm(data)
            if form.is_valid():
                order_item = OrderItem.objects.filter(id=data["orderitem_id"]).first()
                if not (order_item):
                    return Response(
                        {"status": "Bad request", "Reason": "bad order item id"}
                    )
                if order_item.order != basket:
                    return Response(
                        {"status": "Bad request", "Reason": "bad order item id"}
                    )
                quantity = data["quantity"]
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
        basket = list(Order.objects.filter(user=user, state="basket"))[-1]
        if basket:
            OrderItem.objects.filter(order=basket).delete()
            return Response({"status": "OK"})
        else:
            return Response({"status": "No Items"})


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        orders = (
            list(Order.objects.filter(user=user, state="confirmed"))
            + list(Order.objects.filter(user=user, state="new"))
            + list(Order.objects.filter(user=user, state="assembled"))
            + list(Order.objects.filter(user=user, state="sent"))
            + list(Order.objects.filter(user=user, state="delivered"))
        )
        print(orders)
        data = {}
        if orders:
            for i, order in enumerate(orders):
                data[i] = {"order_id": order.id, "order.state": order.state}
            return Response(data)
        else:
            return Response({"status": "You dont't have any orders"})

    def post(self, request, *args, **kwargs):
        user = request.user
        order = list(Order.objects.filter(user=user, state="basket"))
        if order:
            order = order[-1]
            orderitems = list(OrderItem.objects.filter(order=order))
            if orderitems:
                order.state = "new"
                order.save()
                key = ConfirmEmailKey.objects.filter(user=user).first()

                send_mail(
                    "destira@mail.ru",
                    f"http://127.0.0.1:8000/confirm_order/{key.key}/{order.id}/",
                    EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

                return Response({"status": "OK"})
            else:
                return Response({"status": "No items in basket"})
        else:
            return Response({"status": "No basket"})


@api_view()
def confirm_order(request, key, id, *args, **kwargs):
    try:
        user_key = ConfirmEmailKey.objects.filter(key=key).first()
        user = user_key.user
        order = Order.objects.filter(user=user, id=id, state="new").first()
        if order:
            order.state = "confirmed"
            order.save()

            send_mail(
                "destira@mail.ru",
                f"Ваш заказ подтвержен. Его номер {order.id}. Спасибо за выбор нашего сервиса",
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            orderitems = list(OrderItem.objects.filter(order=order))
            for orderitem in orderitems:
                shop_id = orderitem.product_info.shop.id
                staff = [
                    user.email for user in list(User.objects.filter(company_id=shop_id))
                ]
                send_mail(
                    "destira@mail.ru",
                    f"В вашем магазине был совершен заказ на товар: {orderitem.product_info.product.name} в количестве "
                    f"{orderitem.quantity}",
                    EMAIL_HOST_USER,
                    staff,
                    fail_silently=False,
                )

            return Response({"status": "OK"})
        else:
            return Response({"status": "order has already confirmed"})
    except Exception as e:
        return Response(
            {"status.": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

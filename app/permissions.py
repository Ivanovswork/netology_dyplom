import yaml
from .models import Shop
from rest_framework.permissions import BasePermission


class GetShop(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        return False


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        return request.user.is_superuser


class IsStaff(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        with open('./data/shop1.yaml', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            # print(data)

            shop = list(Shop.objects.filter(name=data['shop']))[0]
            print(shop.id)
            print(request.user.company_id)
        return request.user.is_staff and request.user.company_id == shop.id

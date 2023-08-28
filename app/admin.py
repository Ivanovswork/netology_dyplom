from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Param,
    ConfirmEmailKey,
    Contact,
    Order,
    OrderItem,
)


@admin.action(description="Поменять статус 'is_staff'")
def change_is_staff(modeladmin, request, queryset):
    if request.user.is_staff:
        queryset.update(is_staff=False)
    else:
        queryset.update(is_staff=True)


#
# class AddUserForm(forms.ModelForm):
#     password1 = forms.CharField(
#         label='Password', widget=forms.PasswordInput
#     )
#     password2 = forms.CharField(
#         label='Confirm password', widget=forms.PasswordInput
#     )
#
#     class Meta:
#         model = User
#         fields = ('email',)
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Пароли не совпадают")
#         return password2
#
# def save(self, commit=True):
#
#     user = super().save(commit=False)
#     user.set_password(self.cleaned_data["password1"])
#     if commit:
#         user.save()
#     return user


class ContactInline(admin.TabularInline):
    model = Contact
    fields = ["id", "user", "adress", "t_number"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("email", "is_staff", "is_superuser", "company_id", "is_active")
    # list_filter = ('is_staff',)
    # search_fields = ('email', 'company_id')
    # ordering = ('email',)
    # filter_horizontal = ()
    fieldsets = (
        (None, {"fields": ("email", "password", "company_id")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    actions = [change_is_staff]
    inlines = [ContactInline]
    extra = 1


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "status"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 0


class ParamInline(admin.TabularInline):
    model = Param
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    inlines = [ProductInfoInline, ParamInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    list_display = ["id", "product_info", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "data", "state"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product_info", "quantity"]


admin.site.register(Contact)
admin.site.register(ProductInfo)
admin.site.register(Param)
admin.site.register(ConfirmEmailKey)

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, Shop, Category, Product, ProductInfo


@admin.action(description="Поменять статус 'is_staff'")
def change_is_staff(modeladmin, request, queryset):
    if request.user.is_staff:
        queryset.update(is_staff=False)
    else:
        queryset.update(is_staff=True)


class AddUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm password', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2
    #
    # def save(self, commit=True):
    #
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #     return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    form = AddUserForm

    list_display = ('email', 'is_staff', 'is_superuser', 'company_id')
    list_filter = ('is_staff',)
    search_fields = ('email', 'company_id')
    ordering = ('email',)
    filter_horizontal = ()
    actions = [change_is_staff]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class ProductInline(admin.TabularInline):
    model = ProductInfo


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [ProductInline, ]


admin.site.register(ProductInfo)

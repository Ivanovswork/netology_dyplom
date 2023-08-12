from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import CASCADE
from django.contrib.auth.models import PermissionsMixin


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a pasword')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(verbose_name="email", null=False, unique=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=50, validators=[username_validator], blank=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} {self.first_name} {self.last_name}"


class Shop(models.Model):
    name = models.CharField(max_length=30, null=False, verbose_name="Название")
    url = models.URLField(max_length=256, null=False, verbose_name="Cсылка")
    status = models.BooleanField(default=True)
    load_file_name = models.FilePathField(
        path="/python-final-diplom-Ivanovswork/data",
        verbose_name="Абсолютный путь к загрузочному фалу"
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"


    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255, blank=False)
    shop = models.ManyToManyField(Shop, verbose_name="Соответсвующие магазины", related_name="categories")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категори"


    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название", blank=False)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория товаров",
        related_name="Товары",
        on_delete=CASCADE,
        blank=False
    )

    class Meta():
        verbose_name = "Товар"
        verbose_name_plural = "Список товаров"

    def __str__(self):
        return f"{self.name} - {self.category}"


class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="Информация о товаре",
        related_name="info",
        on_delete=CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="products",
        on_delete=CASCADE
    )
    price = models.PositiveIntegerField(verbose_name="Цена", null=False, blank=False)
    quantity = models.PositiveIntegerField(verbose_name="Количество", null=False, blank=False)
    params = models.JSONField()


    class Meta:
        verbose_name = "Информация о товаре"

    def __str__(self):
        return f"{self.product.name} из {self.shop.name}"


class Contact(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Заказ",
        related_name="user",
        on_delete=CASCADE
    )
    adress = models.CharField(verbose_name="Адрес", max_length=255, blank=True)
    t_number = models.CharField(blank=True)



class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Заказ",
        related_name="orders",
        on_delete=CASCADE
    )
    data = models.DateTimeField(verbose_name="Дата заказа", auto_now=True)
    state = models.CharField(verbose_name="Статус", choices=STATE_CHOICES, blank=False, default="new")
    contact = models.ForeignKey(Contact, verbose_name="Доп. информация о пользователе", on_delete=CASCADE)


    class Meta():
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказов"

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Заказ", related_name="item_list", on_delete=CASCADE)

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о товаре",
        related_name="item_list",
        on_delete=CASCADE
    )


    class Meta():
        verbose_name = "Пункт заказа"

    def __str__(self):
        return f"Пункт заказа №{self.order.id} под общим номером {self.id}"



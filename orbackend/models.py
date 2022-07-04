from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

STATE_CHOICES = (
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('dispatched', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class User(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.CharField(max_length=100, verbose_name='email')
    password = models.CharField(max_length=100, verbose_name='Пароль')
    company = models.CharField(max_length=100, verbose_name='Компания')
    position = models.CharField(max_length=50, verbose_name='Должность')


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    building = models.CharField(max_length=100, verbose_name='Дом', blank=True)
    apartment = models.CharField(max_length=50, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=50, verbose_name='Номер телефона')


class Shop(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка на магазин', null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название категории')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True) #?


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    category = models.ForeignKey(Category, verbose_name='Категория товара', related_name='products', on_delete=models.CASCADE)


class ProductInfo(models.Model): #информация о товаре в магазине
    product = models.ForeignKey(Product, verbose_name='Связь с продуктом', related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Связь с магазином', related_name='product_infos', on_delete=models.CASCADE)
    external_id = models.PositiveIntegerField()
    model = models.CharField(max_length=100, verbose_name='Модель', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество единиц товара')
    price = models.PositiveIntegerField(verbose_name='Цена товара')
    price_rrc = models.PositiveIntegerField(verbose_name='Розничная цена товара')


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Заказавший пользователь', related_name='orders', on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, verbose_name='Информация о пользователе', related_name='orders', on_delete=models.CASCADE)
    date_time = models.DateTimeField(verbose_name='Дата и время заказа', auto_now_add=True)
    status = models.CharField(verbose_name='Статус заказа', choices=STATE_CHOICES, max_length=15)


class OrderInfo(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='orders_info', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='orders_info', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Parameter(models.Model):
    name = models.CharField(max_length=200)


class ProductParameter(models.Model):
    product_info = models.ForeignKey(Product, related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'ТОкены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE,
                            verbose_name=('The user which is associated to this password reset token'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Time when the token was generated')
    key = models.CharField('Key', max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {}".format(user=self.user)



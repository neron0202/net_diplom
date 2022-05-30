from django.db import models

STATE_CHOICES = (
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('dispatched', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class User(models.Model):
    surname = models.CharField(max_length=50, verbose_name='Фамилия')
    name = models.CharField(max_length=50, verbose_name='Имя')
    email = models.CharField(max_length=100, verbose_name='email')
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

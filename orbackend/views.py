import yaml

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from django.db.models import Q, Sum, F
from django.db import IntegrityError

from yaml import load, Loader
import requests
from django.http import JsonResponse
from django.core.validators import URLValidator

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Order
from .serializers import UserSerializer, ProductInfoSerializer, ContactSerializer, OrderSerializer
from .signals import new_user_registered, new_order

#4 этап. Регистрация
class AccountRegister(APIView):
    def post(self, request, *args, **kwargs):
        if {'name', 'surname', 'email', 'password', 'company', 'position'}.issubset(request.data):
            errors = {}
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                    return JsonResponse({'Status': False, "Errors": {'password': error_array}})
            else:
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(sender=self.__class__, user_id=user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


#4 этап. Вход
class AccountLogin(APIView):
    def post(self, request,*args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True, 'Token': token.key})
            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


#4 этап. Список товаров --> Карточка товара
class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


#4 этап. Список товаров --> Корзина
class BasketView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in is required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info_product_parameters__parameter').annotate(
            total_sum=Sum('ordered_items__quantity') * F('ordered_items__product_info__price')).distinct()


class OrderView(APIView):
    # 4 Этап. Заказы. Заказ
    def get(self, request, *args, **kwargs):
        if not request.user.is_autenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('order_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # 4 этап. Список товаров --> Подтверждение заказа (левая половина)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'], state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны  все необходимые аргументы'})


class ContactView(APIView):
    # 4 этап. Список товаров --> Подтверждение заказа (правая половина)
    def post(self, request,*args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны  все необходимые аргументы'})


# 3 этап
class GoodsUpload(APIView):
    def post(self, request, *args, **kwargs):
        url = 'https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml'
        stream = requests.get(url).content
        data = yaml.load(stream, Loader=Loader)
        shop, created = Shop.objects.get_or_create(name=data['shop'])
        for category in data['categories']:
            category_object, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            # category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for good in data['goods']:
            product, created = Product.objects.get_or_create(name=good['name'], category_id=good['category'])
            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      model=good['model'],
                                                      external_id=good['id'],
                                                      shop_id=shop.id,
                                                      price=good['price'],
                                                      price_rrc=good['price_rrc'],
                                                      quantity=good['quantity'])
            for name, value in good['parameters'].items():
                parameter_object, created = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                               parameter_id=parameter_object.id,
                                               value=value)
        return JsonResponse({'Status': True})







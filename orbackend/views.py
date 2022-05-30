import yaml
from yaml import load, Loader
import requests
from django.http import JsonResponse
from django.core.validators import URLValidator

from .models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from rest_framework.views import APIView

#https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml

class GoodsUpload(APIView):

    def post(self, request, *args, **kwargs):
        url = request.data.get('https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml')
        validate_url = URLValidator()
        val = validate_url(url)
        print('val=', val)

        stream = requests.get(url).content
        data = yaml.load_yaml(stream, Loader=Loader)
        shop, created = Shop.objects.get_or_create(name=data['name'])
        for category in data['categories']:
            category_object, created = Category.object.get_or_create(id=category['id'], name=category['name'])
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
                ProductParameter.object.create(product_info_id=product_info.id,
                                               parameter_id=parameter_object.id,
                                               value=value)
        return JsonResponse({'Status': True})







from rest_framework import serializers
from .models import User, ProductInfo, Contact, OrderInfo


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user', 'city', 'street', 'building', 'apartment', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'surname', 'email', 'password', 'company', 'position', 'contacts')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    pass


class ProductParameterSerializer(serializers.ModelSerializer):
    pass


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters')
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.modelSerializer):
    class Meta:
        model = OrderInfo
        fields =('id', 'product_info', 'quantity', 'order,')
        read_only_fields = ('id',)
        extra_kwargs = {'order': {'write_only': True}}


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = OrderSerializerfields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact')
        read_only_fields = ('id',)
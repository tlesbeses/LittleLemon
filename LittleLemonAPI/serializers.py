from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category', # Maps category_id back to the category field on saved model
        write_only=True,
        error_messages={
            'does_not_exist': 'The specified category does not exist.'
        }
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user', 'unit_price', 'price']

    def create(self, validated_data):
        # Auto-calculate unit_price and total price based on MenuItem price
        menuitem_id = validated_data.get('menuitem_id')
        menuitem = MenuItem.objects.get(pk=menuitem_id)
        quantity = validated_data.get('quantity')
        
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'total', 'date']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

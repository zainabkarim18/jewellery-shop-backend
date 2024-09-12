from rest_framework import serializers
from .models import Cart, CartItem, Jewellery
# from .models import DeliveryAddress
from .models import Order, Profile, User


class JewellerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Jewellery
        fields = ['id', 'name', 'description', 'price', 'image' , 'stock']

class CartItemSerializer(serializers.ModelSerializer):
    jewellery = JewellerySerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'jewellery', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class SignUpProfileSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = SignUpProfileSerilizer

    def create(self, validated_data):
        return User.objects.create(**validated_data)
    
    class Meta:
        model = User
        fields = ['profile','username']

class ProfileSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    
    def create(self, validated_data):
        User.objects.create()
        return Profile.objects.create(**validated_data)

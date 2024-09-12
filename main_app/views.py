from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView


from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from .models import *
from .serializers import *

from django.apps import apps

# React 
@api_view(['POST'])
def signup(request):
    password = request.data.get('password')
    email = request.data.get('email')
    role = 'user'
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_number = request.data.get('phone_number')
    username = request.data.get('username')

    user = User.objects.create_user(username=username,password=password)
    Profile.objects.create(user=user,first_name=first_name,last_name=last_name,phone_number=phone_number,role=role,email=email)
    Cart.objects.create(user=user)

    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)

# getUser
@api_view(['POST'])
def login_react(request):

    id = get_object_or_404(User, username= request.data.get('username')).id

    userProfile = get_object_or_404(Profile, user_id = id)

    serializer = ProfileSerilizer(userProfile)

    return JsonResponse(serializer.data)

# JEWELLERT
# JEWELLERT LIST
@api_view(['GET'])
def jewellery_react_index(request): 
    jewelleries = Jewellery.objects.all()
    serializer =  JewellerySerializer(jewelleries, many = True)
    return JsonResponse(serializer.data, safe = False)

# JEWELLERY DETAIL
@api_view(['GET'])
def jewellery_react_detail(request, jewellery_id):
    jewellery = Jewellery.objects.get(id=jewellery_id)
    serializer =  JewellerySerializer(jewellery)
    return JsonResponse(serializer.data, safe = False)

# CART
# ADD TO CART
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_jewellery_to_cart(request):
    user = request.user
    jewellery_id = request.data.get('jewellery')
    quantity = int(request.data.get('quantity', 1))
    
    if quantity < 1:
        return Response({"error": "Quantity must be at least 1"})
    

    cart, created = Cart.objects.get_or_create(user=user)
    jewellery = get_object_or_404(Jewellery, id=jewellery_id)

    if quantity > jewellery.stock:
        return Response({"error": "Not enough stock available"})

    cart_item, created = CartItem.objects.get_or_create(cart=cart, jewellery=jewellery)
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()
    
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

# UPDATE JEWELLERY IN CART
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_jewellery_in_cart(request, jewellery_id):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_item = get_object_or_404(CartItem, cart=cart, jewellery_id=jewellery_id)
    jewellery = get_object_or_404(Jewellery, id=jewellery_id)

    new_quantity = request.data.get('quantity', cart_item.quantity)  
    if new_quantity > jewellery.stock:
        return Response({'error': 'Not enough stock available.'})

    serializer = CartItemSerializer(cart_item, data={'quantity': new_quantity}, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors)

# DELETE JEWELLERY FROM CART
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_jewellery_from_cart(request, jewellery_id):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart does not exist.'})

    try:
        cart_item = CartItem.objects.get(cart=cart, jewellery_id=jewellery_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Jewellery not found in cart.'})

    cart_item.delete()
    return Response({'error': 'Jewellery not found.'})

# REMOVE JEWELLERY FROM CART
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_jewellery_from_cart(request, jewellery_id):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart does not exist.'})

    try:
        cart_item = CartItem.objects.get(cart=cart, jewellery_id=jewellery_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Jewellery not found in cart.'})

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        return Response({'message': 'Quantity decreased by one.'})
    else:
        cart_item.delete()
        return Response({'message': 'Jewellery removed from cart.'})

# USER CART
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    user = request.user
    
    cart = Cart.objects.filter(user=user).first()  
    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
        items_data = []

        for item in cart_items:
            jewellery = item.jewellery
            quantity = item.quantity
            
            if quantity > jewellery.stock:
                if jewellery.stock > 0:
                    item.quantity = jewellery.stock

                    item.save()

                    items_data.append({
                        'jewellery_id': jewellery.id,
                        'jewellery_name': jewellery.name,
                        'quantity': jewellery.stock,
                        'price': str(jewellery.price),
                    })
                else:
                    item.delete()
            else:
                items_data.append({
                    'jewellery_id': jewellery.id,
                    'jewellery_name': jewellery.name,
                    'quantity': quantity,
                    'price': str(jewellery.price),
                })

        return Response({'cart_items': items_data})
    
    return Response({'message': 'Cart is empty.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    user = request.user
    if user.is_authenticated:
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            return Response({'message': 'Cart cleared successfully'})
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'})
    return Response({'error': 'User not authenticated'})


# ORDER 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    order_data = request.data

    cart_items = order_data.get('cart')
    if not cart_items:
        return Response({'cart': 'This field is required.'})

    if not isinstance(cart_items, list):
        return Response({'cart': 'Expected list of objects.'})
    
    total_price = 0
    for item in cart_items:
        jewellery_id = item.get('jewellery_id')
        quantity = item.get('quantity')
        if not jewellery_id or not quantity:
            return Response({'cart': 'Each item in the cart must include a jewellery_id and quantity.'})
        
        try:
            jewellery = Jewellery.objects.get(id=jewellery_id)
        except Jewellery.DoesNotExist:
            return Response({'cart': f'Jewellery with ID {jewellery_id} does not exist.'})
        
        if jewellery.stock < quantity:
            return Response({'cart': f'Not enough stock for Jewellery with ID {jewellery_id}.'})

        total_price += jewellery.price * quantity

        jewellery.stock -= quantity
        jewellery.save()
        

        if jewellery.stock == 0:
            jewellery.delete()
    
    order = Order.objects.create(user=request.user, total_price=total_price)
    
    return Response({'message': 'Order placed successfully.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    user = request.user 

    if not user.is_authenticated:
        return Response({"error": "Authentication required."})

    Order = apps.get_model('main_app', 'Order') 
    orders = Order.objects.filter(user=user)  

    orders_data = [
        {
            'id': order.id,
            'total_price': str(order.total_price), 
            'order_date': order.order_date.isoformat(), 
        } for order in orders
    ]

    return Response(orders_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details(request, order_id):
    user = request.user

    if not user.is_authenticated:
        return Response({"error": "Authentication required."})

    Order = apps.get_model('main_app', 'Order')
    Cart = apps.get_model('main_app', 'Cart')

    try:
        order = Order.objects.get(id=order_id, user=user)

        order_data = {
            'id': order.id,
            'total_price': str(order.total_price),
            'order_date': order.order_date,
        }

        cart_data = None
        if order.cart:
            cart = Cart.objects.get(id=order.cart.id)
            total_price = sum(item.jewellery.price * item.quantity for item in cart.items.all())
            cart_data = {
                'id': cart.id,
                'items': [
                    {
                        'id': item.id,
                        'jewellery_id': item.jewellery.id,
                        'jewellery_name': item.jewellery.name,
                        'quantity': item.quantity,
                        'price': str(item.jewellery.price),
                        'total': str(item.jewellery.price * item.quantity)
                    }
                    for item in cart.items.all()
                ],
                'total_price': str(total_price)
            }

        order_data['cart'] = cart_data

        return Response(order_data)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.user != order.user:
        return Response({'error': 'You do not have permission to delete this order.'})
    
    order.delete()
    return Response({'message': 'Order has been successfully deleted.'})


# Django
def home(request):
    return render(request, 'home.html')

class Home(LoginView):
    template_name = 'home.html'

@login_required
def jewellery_index(request): 
    jewelleries = Jewellery.objects.all()
    user = request.user
    profile = get_object_or_404(Profile, user_id=user.id)
    if profile.role == 'admin' or profile.role == 'Admin':
        return render(request, 'jewellery/index.html',{'jewelleries': jewelleries})

@login_required
def jewellery_detail(request, jewellery_id):
    jewellery = Jewellery.objects.get(id=jewellery_id)
    user = request.user
    profile = get_object_or_404(Profile, user_id=user.id)
    if profile.role == 'admin' or profile.role == 'Admin':
        return render(request, 'jewellery/detail.html', {'jewellery': jewellery})

class JewelleryCreate(LoginRequiredMixin,CreateView):
    model = Jewellery
    fields = '__all__'

    def form_valid(self, form):
        # username = form.cleaned_data['user']
        # user = get_object_or_404(User,username = username)
        # profile = get_object_or_404(Profile, user_id = user.id)
        user = self.request.user
        profile = get_object_or_404(Profile, user_id=user.id)

        if profile.role == 'admin' or profile.role == 'Admin':
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

class JewelleryUpdate(LoginRequiredMixin,UpdateView):
    model = Jewellery
    fields = ['name', 'description', 'price', 'image','stock']

    def form_valid(self, form):
            user = self.request.user
            profile = get_object_or_404(Profile, user_id=user.id)

            if profile.role == 'admin' or profile.role == 'Admin':
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

class JewelleryDelete(LoginRequiredMixin,DeleteView):
    model = Jewellery
    success_url = '/jewellery'

    def form_valid(self, form):
            user = self.request.user
            profile = get_object_or_404(Profile, user_id=user.id)

            if profile.role == 'admin' or profile.role == 'Admin':
                return super().form_valid(form)
            else:
                return super().form_invalid(form)    

@login_required
def list_all_orders(request):
    orders = Order.objects.all()
    user = request.user
    profile = get_object_or_404(Profile, user_id=user.id)
    if profile.role == 'admin' or profile.role == 'Admin':
        return render(request, 'order/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    cart_items = order.cart.items.all() if order.cart else []
    user = request.user
    profile = get_object_or_404(Profile, user_id=user.id)
    if profile.role == 'admin' or profile.role == 'Admin':
        return render(request, 'order/order_detail.html', {
            'order': order,
            'cart_items': cart_items,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone_number': profile.phone_number
        })

class OrderDelete(DeleteView):
    model = Order
    success_url = '/orders'

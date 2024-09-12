from django.urls import path
from . import views


urlpatterns = [

    # Django 
    path('', views.Home.as_view(), name='home'),
    path('jewellery/', views.jewellery_index, name='jewellery-index'),
    path('jewellery/<int:jewellery_id>/', views.jewellery_detail, name='jewellery-detail'),
    path('jewellery/create/', views.JewelleryCreate.as_view(), name='jewellery-create'),
    path('jewellery/<int:pk>/update/', views.JewelleryUpdate.as_view(), name='jewellery-update'),
    path('jewellery/<int:pk>/delete/', views.JewelleryDelete.as_view(), name='jewellery-delete'),

    # ORDER 
    path('orders/', views.list_all_orders, name='list-all-orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
    path('orders/<int:pk>/delete/', views.OrderDelete.as_view(), name='order-delete'),
    
    # React 
    path('api/login/', views.login_react, name='login-react'),
    path('api/accounts/signup/', views.signup, name='signup'),


    path('api/jewellery/', views.jewellery_react_index, name='jewellery-react-index'),
    path('api/jewellery/<int:jewellery_id>/', views.jewellery_react_detail, name='jewellery-react-detail'),

    # CART
    path('api/carts/', views.view_cart, name='view-cart'),
    path('api/carts/add/jewellery/', views.add_jewellery_to_cart, name='add-jewellery-to-cart'),
    path('api/carts/delete/jewellery/<int:jewellery_id>/', views.delete_jewellery_from_cart, name='delete-jewellery-from-cart'),
    path('api/carts/remove/jewellery/<int:jewellery_id>/', views.remove_jewellery_from_cart, name='remove-jewellery-from-cart'),
    path('api/carts/update/jewellery/<int:jewellery_id>/', views.update_jewellery_in_cart, name='update-jewellery-in-cart'),
    path('api/carts/clear/', views.clear_cart, name='clear-cart'),

    # ORDER
    path('api/orders/add/', views.place_order, name='place-order'),
    path('api/orders/', views.get_user_orders, name='get-user-orders'),
    path('api/orders/<int:order_id>/', views.order_details, name='order-details'),
    path('api/orders/delete/<int:order_id>/', views.delete_order, name='delete-order'),

]
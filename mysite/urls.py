from django.urls import path
from . import views

urlpatterns = [
    path('', views.grocery_store, name='grocery_store'),
    path('productview/<int:product_id>/', views.product_view, name='product_view'),
    path('viewcart/', views.view_cart, name='view_cart'),
    path('viewaddedproducts/', views.view_added_products, name='view_added_products'),
    path('view_product_orders/<str:encoded_product_id>/', views.view_product_orders, name='view_product_orders'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('addtocart', views.addtocart, name='addtocart'),
    path('add_address', views.add_address, name='add_address'),
    path('update_user_info', views.update_user_info, name='update_user_info'),
    path('update_user_address', views.update_user_address, name='update_user_address'),
    path('update_order', views.update_order, name='update_order'),
    path('update_product', views.update_product, name='update_product'),
    path('addproduct', views.addproduct, name='addproduct'),
    # Define other app-specific URL patterns here if needed
]
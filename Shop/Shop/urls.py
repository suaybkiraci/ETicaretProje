"""
URL configuration for Shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from Products.views import (
    homepage, login_view, signup_view, products,CustomPasswordResetView, product_list, get_image, 
    dashboard, logout_view, add_to_cart,profile, view_cart, checkout, remove_product
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('add/', products, name='add_product'),
    path('list/', product_list, name='product_list'),
    path('image/<str:image_id>/', get_image, name='get_image'),

    # sepet işlemelri
    path('add_to_cart/<str:user_id>/<str:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('remove_product/<str:product_id>/', remove_product, name='remove_product'),
    
    #profil işlemleeri
    path('profile/',profile,name='profile'),

    #şifre formu
    path('password_reset/',CustomPasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
]

from django.shortcuts import render, redirect
from .models import Product,Cart
from .forms import ProductForm,ProfileForm
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine import connect,DoesNotExist
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from bson.objectid import ObjectId
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from Shop.settings import mongodbname
from mongoengine import connect
# Create your views here.
db=connect(mongodbname,host="localhost",port=27017)

def homepage(request):
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'homepage.html')

def login_view(request):
    
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            # Hatalı giriş durumu
            return render(request, 'login.html', {'error': 'Kullanıcı adı veya şifre hatalı!'})
    
    return render(request, 'login.html')

def signup_view(request):
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Kullanıcı adı ve şifre doğrulama
        if not username or not password:
            messages.error(request, "Kullanıcı adı ve şifre gerekli.")
            return redirect('signup')

        # yeni kullanıcı
        try:
            user = User.objects.create_user(username=username,password=password)
            user.save()
            messages.success(request, "Hesabınız başarıyla oluşturuldu!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('homepage')

@login_required(login_url='login')
def product_list(request):
    products = Product.objects.all()
    for product in products:
        if product.image and product.image.grid_id:
            product.image_id = str(product.image.grid_id)
        else:
            product.image_id = ''
    return render(request, 'product_list.html', {'products': products,'user.id':str(request.user.id)})

@login_required(login_url='login')
def products(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = Product(
                name=form.cleaned_data['name'],
                price=form.cleaned_data['price'],
                description=form.cleaned_data['description']
            )
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required(login_url='login')
def add_to_cart(request, user_id, product_id):
    if request.method == 'POST':
        try:
            user_id = str(request.user.id)  
            product = Product.objects.get(id=product_id)
            cart = Cart.objects(user_id=user_id).first()
            
            # Sepet yoksa yeni oluştur
            if not cart:
                cart = Cart(user_id=user_id, products=[], quantities=[], total_price=0)
                cart.save()
            
            quantity = int(request.POST.get('quantity', 1))
            
            # Ürünü sepete ekleme 
            existing_index = next((i for i, p in enumerate(cart.products) if str(p.id) == product_id), None)
            
            if existing_index is not None:
                cart.quantities[existing_index] += quantity
            else:
                cart.products.append(product)
                cart.quantities.append(quantity)
            
            cart.update_total_price()
            cart.save()
            
            messages.success(request, 'Ürün sepete eklendi!')
            return redirect('cart')
        
        except Product.DoesNotExist:
            messages.error(request, 'Ürün bulunamadı!')
            return redirect('product_list')
        
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
            return redirect('product_list')
    
    messages.error(request, 'Geçersiz istek metodu!')
    return redirect('product_list')

def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Kullanıcı giriş yapmamışsa yönlendir

    user_id = str(request.user.id)  # Giriş yapan kullanıcının ID'si
    try:
        # MongoDB sorgusu: Sepeti kullanıcının ID'sine göre getir
        cart = Cart.objects(user_id=user_id).first()
        print("debug cart obj",repr(cart))
        if not cart:
            cart=Cart(user_id=user_id,products=[],quantities=[],total_price=0)
            cart.save()
        # Sepetteki ürünlerin bilgilerini hazırlıyoruz
        products_info = [{
            'product_id': str(product.id),
            'product_name': product.name,
            'quantity': quantity,
            'price': product.price,
            'total': product.price * quantity
        } for product, quantity in zip(cart.products, cart.quantities)]

        return render(request, 'cart.html', {'products': products_info, 'total_price': cart.total_price})

    except DoesNotExist:
        # Sepet bulunamadıysa, kullanıcıya mesaj göster
        return render(request, 'cart.html', {'message': 'Sepetinizde ürün bulunmamaktadır.'})
def checkout(request):
    if request.method == 'POST':
        # Ödeme işlemi
        return redirect('thanks')
    return render(request, 'checkout.html')
def thanks(request):
    return render(request, 'thanks.html')
def remove_product(request,product_id):
    user_id=str(request.user.id)
    try:
        cart=Cart.objects(user_id=user_id).first()
        product=Product.objects.get(id=product_id)
        cart.remove_product(product)
        messages.success(request, f"“{product.name}” sepetten çıkarıldı.")
    except(Cart.DoesNotExist,Product.DoesNotExist):
        messages.error(request,"Ürün veya sepet bulunamadı")
    return redirect('cart')
@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        p_form=ProfileForm(request.POST,instance=request.user)
        pwd_form=PasswordChangeForm(user=request.user,data=request.POST)
        if 'update_profile' in request.POST and p_form.is_valid():
            p_form.save()
            messages.success(request,"Profil bilgileriniz güncellendi")
            return redirect('profile')
        if 'change_password' in request.POST and pwd_form.is_valid():
            user=pwd_form.save()
            update_session_auth_hash(request,user)
            messages.success(request,"Parolanız güncellendi")
            return redirect('profile')
    else:
        p_form=ProfileForm(instance=request.user)
        pwd_form=PasswordChangeForm(user=request.user)
    return render(request,'profile.html',{'p_form':p_form,'pwd_form':pwd_form})

class CustomPasswordResetView(PasswordResetView):
    template_name='emails/password_reset_form.html'
    success_url=reverse_lazy('password_reset_done')
    email_template_name='emails/password_reset_email.html'
    subject_template_name='emails/password_reset_subject.txt'

    def send_mail(self,subject_template_name,email_template_name,context,from_email,to_email,html_email_template_name=None):
        subject=render_to_string(subject_template_name,context).strip()
        body_text=render_to_string(email_template_name,context)
        html_body=render_to_string('emails/password_reset_email.html',context)

        email=EmailMultiAlternatives(subject,body_text,from_email,[to_email])
        email.attach_alternative(html_body,'text/html')
        num_sent=email.send()
        print("DEBUG: Emails sent: ",num_sent)

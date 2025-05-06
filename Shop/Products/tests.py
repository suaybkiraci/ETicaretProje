from django.test import TestCase
from .models import Product, Cart
from django.urls import reverse
from Shop.settings import mongodbname
from mongoengine import connect
from django.test import Client
from django.contrib.auth.models import User


connect(mongodbname,host="localhost",port=27017)   #test için ayrı bir veritabanına bağlanma
# Create your tests here.

class ProductTests(TestCase):  #ürün testleri
    def test_product_creation(self):   ## bir product nesnesi oluşturma testi
        product = Product(name="Test Product", price=100, description="Test Description")
        product.save()
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.price, 100)
        self.assertEqual(product.description, "Test Description")
       ##  self.assertEqual(product.image, "sadasda")   image bölümüne string veri atarsak failure oluyoruz


class CartTests(TestCase):  #sepet testleri
    def test_cart_creation(self):    #bir sepet nesnesi oluştuma testi
        cart = Cart(user_id="1", products=[], quantities=[], total_price=0)  # ürün ve sayı eklemediğimizde de sıkıntı çıkmıyor
        cart.save()
        self.assertEqual(cart.user_id, "1")
        self.assertEqual(cart.products, [])
        self.assertEqual(cart.quantities, [])
        self.assertEqual(cart.total_price, 0)

    def test_add_product(self):   #sepete bir ürün ekleme testi
        product = Product(name="Test Product", price=100, description="Test Description")  #örnek ürün
        product.save()
        cart = Cart(user_id="1", products=[], quantities=[], total_price=0)   #örnek sepet
        cart.add_product(product, 1)       #ürünü sepete ekleme
        self.assertEqual(cart.products[0], product)
        self.assertEqual(cart.quantities[0], 1)

    def test_remove_product(self):   #sepetten bir ürün silme testi
        product = Product(name="Test Product", price=100, description="Test Description")  #örnek ürün
        product.save()
        cart = Cart(user_id="1", products=[], quantities=[], total_price=0)   #örnek sepet
        cart.add_product(product, 1)       #ürünü sepete ekleme
        cart.remove_product(product)      #ürünü sepetten silme
        self.assertEqual(cart.products, [])    #sepet boş mu

    def test_update_total_price(self):   #sepetin toplam fiyatını güncellemesi testi
        product = Product(name="Test Product", price=100, description="Test Description")  #örnek ürün
        product2 = Product(name="Test Product2", price=200, description="Test Description2")  #örnek ürün
        product.save()
        product2.save()
        cart = Cart(user_id="1", products=[], quantities=[], total_price=0)   #örnek sepet
        cart.add_product(product, 1)       #ürünü sepete ekleme
        cart.add_product(product2, 1)      #ürünü sepete ekleme
        cart.update_total_price()         #sepetin toplam fiyatını güncellemesi
        self.assertEqual(cart.total_price, 300)


#Wiew Testleri
class HomepageTests(TestCase):
    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)  #sayfa geldi mi
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'},follow=True)  #post request ile login 
        self.assertEqual(response.status_code, 200) #login başarılı mı

    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('signup'), {'username': 'testuser', 'password': 'testpassword'},follow=True) 
        self.assertEqual(response.status_code, 200) 
        self.assertRedirects(response, reverse('login'))  #signup yapıldıktan sonra login sayfasına yönlendiriyor mu

    def test_dashboard(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'),follow=True)
        self.assertEqual(response.status_code, 200) 

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.logout()
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)


class ProductandCartWiewTests(TestCase):
    def setUp(self):   #giriş yapılması gerekli olan fonksiyonlar için örnek kullanıcı oluşturma
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')  #test yaptığımız fonksiyonlar loginrequired olduğu için login yapıyoruz

    def test_product_list(self):  #ürün listesi görüntüleme testi
        product = Product(name="Test Product", price=100, description="Test Description")
        product.save()
        response = self.client.get(reverse('product_list'))   #ürün listesini görüntüleme
        self.assertEqual(response.status_code, 200)   #200 döndüyse başarılı
        self.assertContains(response, "Test Product")   #ürün listesinde Test Product var mı

    def test_products(self):  #ürün ekleme testi
        product = Product(name="Test Product", price=100, description="Test Description")
        product.save()
        response = self.client.get(reverse('add_product'))   
        self.assertEqual(response.status_code, 200)   
    
    def test_add_to_cart_and_remove_product(self):  #sepete ürün ekleme ve silme testi , iki fonksiyon testini birleştirdik 
        product = Product(name="Test Product", price=100, description="Test Description")  #ürün oluşturduk
        product.save()
        cart = Cart(user_id="1", products=[], quantities=[], total_price=0)  #sepet oluşturduk
        cart.save()
        cart.add_product(product,1)#ürünü sepete ekledik
        self.assertEqual(cart.products[0], product)  #ürün sepette var mı ve diğer parametreler doğru kaydedilmiş mi
        self.assertEqual(cart.quantities[0], 1)  
        self.assertEqual(cart.total_price, 100)  
        cart.remove_product(product)#ürünü sepetten sildik
        self.assertEqual(cart.products, [])    #sepet boş mu

    def test_view_cart(self):  #sepeti görüntüleme testi   #sepet boşken de görüntülüme yapılabilmel
        response = self.client.get(reverse('cart'))  
        self.assertEqual(response.status_code, 200)
    
    def test_checkout(self):  #ödeme ekranıtesti
        response = self.client.get(reverse('checkout'))  
        self.assertEqual(response.status_code, 200)

    def test_thanks(self):  #ödeme sonrası sayfa testi 
        response = self.client.get(reverse('thanks'))  
        self.assertEqual(response.status_code, 200)

class ProfileTests(TestCase):
    def setUp(self):   
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_profile(self):   
        response = self.client.get(reverse('profile'))  
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):  #profil bilgilerini güncelleme testi
        response = self.client.post(reverse('profile'), {'update_profile': 'update_profile', 'first_name': 'Test', 'last_name': 'User','email': 'test@test.com'},follow=True)
        self.assertEqual(response.status_code, 200)  #başarıyla post edildi mi

        self.user.refresh_from_db()  #veritabanındaki kullanıcı bilgilerini güncelle
        self.assertEqual(self.user.first_name, 'Test')  #güncellenen bilgiler doğru mu
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'test@test.com')
        self.assertContains(response, 'Profil bilgileriniz güncellendi')
    
class PasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        def test_change_password(self):  #şifre değiştirme testi
            response = self.client.post(reverse('profile'), {'change_password': 'change_password', 'old_password': 'testpassword', 'password1': 'newpassword', 'password2': 'newpassword'},follow=True)
            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db() 
            self.assertTrue(self.user.check_password('newpassword'))  #yeni şifre ile aynı mı
            self.assertContains(response, 'Parolanız güncellendi')

            self.client.logout()
            self.client.login(username='testuser', password='newpassword') #yeni şifre ile login yapılabiliyor mu
            self.assertEqual(response.status_code, 200)










































        
        

        



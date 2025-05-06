from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import uuid
from django.contrib.auth.models import User
from mongoengine import connect, disconnect


class BaseTest(unittest.TestCase):   #diğer testlerde kullanılacak olan temel sınıf
    def setUp(self):   #test etmek için giriş yapılmasını sağlayan başlangıç fonksiyonu
        disconnect()
        connect("eticaret_test_db",host="localhost",port=27017,alias="test_db")
        options = webdriver.ChromeOptions()  
        options.add_argument("--incognito")   #tarayıcıyı yeni bir oturumda açar çünkü testler arasında tarayıcı oturumları çakışıyormuş çok hata aldım
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://localhost:8000")
        self.username = f"testuser_{uuid.uuid4().hex[:6]}"   #her test için farklı kullanıcı adı oluşturr
        self.password = "Testpass123!"
        User.objects.filter(username=self.username).delete()    #varsa eğer bu kullanıcı kayıt olurken sıkıntı çıkmasın diye siler

    def tearDown(self):     #testler bittikten sonra çalışacak fonksiyon
        User.objects.filter(username=self.username).delete()     #databaseden test kullanıcısını siler
        from mongoengine.connection import get_db
        db=get_db("test_db")
        db.client.drop_database("test_db")
        disconnect()
        
        self.driver.quit()    #tarayıcıyı kapatır

class UserRegistrationTest(BaseTest):
    def test_register_and_login(self):
        wait = WebDriverWait(self.driver, 15)    #bekleme fonksiyonu
        
       
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Kayıt Ol"))).click()   #kayıt ol butonu görünene kadar bekler ve görününce tıklar
        wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(self.username)   #aynı şekilde username için
        self.driver.find_element(By.ID, "password").send_keys(self.password)  
        self.driver.find_element(By.NAME, "submit").click()
        
       
        wait.until(EC.url_contains("/login"))    #url içinde login kelimesi görünene kadar bekler
        
        
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "submit").click()
        
        
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Çıkış Yap")))    #çıkış yap butonu görünene kadar bekler bu sayede giriş yapıldığını anlarız

class AddProductToCartTest(BaseTest):
    def setUp(self):
        super().setUp()
        
        User.objects.create_user(username=self.username, password=self.password)
        self.driver.get("http://localhost:8000/login")
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "submit").click()
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, "Çıkış Yap")))

    def test_add_product_to_cart(self):
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.element_to_be_clickable((By.NAME, "Ürün Ekle"))).click()
        wait.until(EC.visibility_of_element_located((By.NAME, "name"))).send_keys("test_product")
        self.driver.find_element(By.NAME, "price").send_keys("100")
        self.driver.find_element(By.NAME, "description").send_keys("Test desc")
        self.driver.find_element(By.NAME, "submit").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(., 'test_product')]")))


if __name__ == "__main__":
    unittest.main()
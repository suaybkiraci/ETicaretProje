from mongoengine import Document,IntField, StringField,ImageField, FloatField,DateTimeField, ReferenceField, IntField, EmbeddedDocument, EmbeddedDocumentListField, ListField, CASCADE, FileField
from mongoengine.document import Document
from django.contrib.auth.models import User
from datetime import datetime
from Shop.settings import mongodbname

from mongoengine import connect
connect(mongodbname,host="localhost",port=27017)

# Create your models here.

class Product(Document):
    name = StringField(max_length=100, required=True)
    price = FloatField(required=True)
    description = StringField(max_length=500, required=True)
    image = ImageField(thumbnail_size=(300,300))
    created_at = DateTimeField(default=datetime.now)


    def __str__(self):
        return self.name

class Cart(Document):
    user_id=StringField(required=True)
    products=ListField(ReferenceField(Product))
    quantities=ListField(IntField(default=1))
    total_price=FloatField(default=0.0)
    created_at=DateTimeField(default=datetime.now)
    

    def add_product(self, product,quantity):
        if product not in self.products:
            self.products.append(product)
            self.quantities.append(quantity)
        else:
            index=self.products.index(product)
            self.quantities[index]+=quantity
        self.update_total_price()
        self.save()

    def remove_product(self,product):
        if product in self.products:
            index=self.products.index(product)
            self.products.pop(index)
            self.quantities.pop(index)
            self.update_total_price()
            self.save()


    
    def update_total_price(self):
        self.total_price=sum(product.price*quantity for product,quantity in zip(self.products,self.quantities))
        self.save()
    def __str__(self):
        return f"Sepet: {self.user_id}, {len(self.products)} ürün"

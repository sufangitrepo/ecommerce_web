from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator 
# Create your models here.
def upload_url(model, str):
        print(model)
        print(str)
        return 'assets/images/' + str
class Category(models.Model):

    
    name = models.CharField(max_length=100, unique=True)
    img = models.ImageField(upload_to='assets/images/', null=True)
    offer = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=0)

class OfferByCategory(models.Model):
    off_by_category = models.DecimalField(decimal_places=2,max_digits=10)
    category = models.OneToOneField(to=Category, on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10, default=0)
    img = models.ImageField(upload_to='assets/images')
    
class Rating(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    rating = models.DecimalField(decimal_places=1, max_digits=1,
                                  validators=[MinValueValidator(1), MaxValueValidator(5)])

class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(decimal_places=1, max_digits=40, default=0)

class CartItem(models.Model):
    cart = models.ForeignKey(to=Cart, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField()
    amount = models.DecimalField(decimal_places=1, max_digits=40, default=0)


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(decimal_places=1, max_digits=20)
    

class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField()
    price = models.DecimalField(decimal_places=1, max_digits=10)

    
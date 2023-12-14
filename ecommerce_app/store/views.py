from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import *


def index_view(request):
    objects = Category.objects.all()
    user = request.user
    username = user.username
    if  not user or user.is_anonymous:
        username = None 

    return render(request=request, template_name='index.html', context={'categories': objects, 'user': username})

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username:
            return render(request, 'signup.html')
        if not password:
            return render(request, 'signup.html')
        user = User(username=username)
        user.set_password(password)
        user.save()
        cart = Cart()
        cart.user = user
        cart.save()
        return render(request, 'login.html')
    else:
        return render(request, 'signup.html')

# login page
def user_login(request):
    if request.user or not request.user.is_anonymous:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username:
            return render(request, 'login.html', context={'error':"email is reuired"})
        if not password:
            return render(request, 'login.html', context={'error':"password is required"})
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  
            
            username = user.username
            if  not user or user.is_anonymous:
                username = None 
            objects = Category.objects.all()  
            return render(request, 'index.html', context={user:username,'categories': objects}, )
        else:
            return render(request, 'login.html', context={'error':"something went wrong",})
                
    else:
        return render(request, 'login.html')

# logout page
def user_logout(request):
    logout(request)
    return redirect('login')

def products(request, id):
    category = Category.objects.filter(id=id).first()
    if not category:
        return render(request, '404.html', )
    products = Product.objects.filter(category=category)
    return render(request, 'products.html', context={'products': products, 'category':category.name})

def search_products(request):
    search_value = request.GET.get('search')
    products = None
    if search_value:
        products = Product.objects.filter(name__icontains=search_value)
    else:
        products = Product.objects.all()    
    return render(request, 'products.html', context={'products': products, 'category':''})

def add_to_cart(request, id):

    user = request.user
    if not user or user.is_anonymous:
        return redirect('login')
    product = None
    try:
        product = Product.objects.get(id=id)
        cart = Cart.objects.filter(user=user).first()
        db_item = CartItem.objects.filter(Q(cart=cart) & Q(product=product)).first()
        if db_item:
            return redirect(f'/app/products/{product.category.id}')

    except Product.DoesNotExist:
        return render(request, '404.html', )
    cart: Cart = Cart.objects.filter(user=user).first()
    try:
        if cart:
            new_item = CartItem()
            new_item.product = product
            new_item.qty = 1
            new_item.cart=cart
            new_item.amount = product.price
            new_item.save()

            cart_items = CartItem.objects.filter(cart=cart)
            total = 0
            for cart_it in cart_items:
                total = total + cart_it.product.price
            cart.total = total
            cart.save()    

        else:
            print('user')
            new_cart: Cart = Cart()
            new_cart.user = user
            new_cart.save()
            cart_item: CartItem = CartItem()
            cart_item.product = product
            cart_item.qty = 1
            cart_item.cart=new_cart
            cart_item.amount = product.price
            cart_item.save()
            cart_items = CartItem.objects.filter(cart=new_cart)
            total = 0
            for cart_it in cart_items:
                total = total + cart_it.product.price 
            new_cart.total = total
            new_cart.save()
    except Exception as e:
        print(e)
        return redirect('login')
    return redirect(f'/app/products/{product.category.id}')

def cart(request):
    user = request.user
    if not user or user.is_anonymous:
        return redirect('login')
    cart = Cart.objects.filter(user=user).first()
    cart_items = []
    if cart: 
      cart_items = CartItem.objects.filter(cart=cart.id)
    return render(request, 'cart.html', context={'cartItems': cart_items, 'cart':cart })


def place_order(request, cart):
    user = request.user
    if not user or user.is_anonymous:
        return redirect('login')
    cart = Cart.objects.filter(id=cart).first()
    cart_items = CartItem.objects.filter(cart=cart)
    order = Order.objects.create(user=user, total_price=cart.total)
    OrderItem.objects.bulk_create([OrderItem(product=cart_item.product,
                                                             order=order,
                                                               qty=cart_item.qty,
                                                                 price=cart_item.amount)
                                                                   for cart_item in cart_items ])
    cart.delete()
    return redirect('index')

def delete_cart_item(request, id):
    try:
        item = CartItem.objects.get(id=id)
        cart = Cart.objects.get(id=item.cart.id)
        cart.total -= item.amount
        cart.save()
        item.delete()
    except CartItem.DoesNotExist:
        return render(request, '404.html', )
    return redirect('addCart')

def increment(request, id):
    try:
        item = CartItem.objects.get(id=id)
        item.qty += 1
        item.save()
        cart = Cart.objects.get(id=item.cart.id)
        cart.total += item.product.price
        cart.save()
    except CartItem.DoesNotExist:
        return render(request, '404.html', )
    return redirect('addCart')

def decrement(request, id):
    try:
        item = CartItem.objects.get(id=id)
        if item.qty == 1 :
            return redirect('addCart')
        item.qty -= 1
        item.save()
        cart = Cart.objects.get(id=item.cart.id)
        cart.total -= item.product.price
        cart.save()
    except CartItem.DoesNotExist:
        return render(request, '404.html', )
    return redirect('addCart')

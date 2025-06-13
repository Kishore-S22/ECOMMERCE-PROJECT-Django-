from django.shortcuts import render,redirect
from .models import *
from shop.form import CustomerUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json
from django.db.models import Q

# Create your views here.

def home(request):
    products = Product.objects.filter(trending=1)
    return render (request,'shop/index.html',{'products':products})


def search_view(request):
    query = request.GET.get('query')
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(vendor__icontains=query) |
            Q(category__name__icontains=query),
            status=0
        )
    return render(request, 'shop/search_results.html', {'products': products, 'query': query})




def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,'shop/fav.html',{'fav':fav})
    else:
        return redirect("/")
    

def remove_fav(request,fid):
    item=Favourite.objects.get(id=fid)
    item.delete()
    return redirect('/favviewpage')

def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')


def fav_page(request):
    if request.headers.get('X-Requested-With')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data= json.load(request)
            product_id=data['pid']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Favourite'},status=200)
                else:
                    Favourite.objects.create(user=request.user,product_id=product_id)
                    return JsonResponse({'status' : 'Product Added to Favourite'},status=200)
                            # 
        else:
            return JsonResponse({'status' : 'Login to Add Favourite'},status=200)
    else:
        return JsonResponse({'status' : 'Invalid Access'},status=200)

def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,'shop/cart.html',{'cart':cart})

def add_to_cart(request):
    if request.headers.get('X-Requested-With')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data= json.load(request)
            product_qty=data['product_qty']
            product_id=data['pid']
            # print(request.user.id)
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Cart'},status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status':'Product Added To Cart'},status=200)
                    else:
                        return JsonResponse({'status':'Product Stock Not Available'},status=200)
                        
        else:
            return JsonResponse({'status' : 'Login to Add Cart'},status=200)
    else:
        return JsonResponse({'status' : 'Invalid Access'},status=200)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is  not None:
                login(request,user)
                messages.success(request,'Logged in Successfully')
                return redirect('/')
            else:
                messages.error(request,'invalid username or password')
                return redirect('/login')
        return render(request,'shop/login.html')
    

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Logged out Successfully')
    return redirect('/')
        

def register(request):
    form=CustomerUserForm()
    if request.method=='POST':
        form=CustomerUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Registration Success You Can Login')
            return redirect('/login')
    return render(request, 'shop/register.html', {'form':form})

def collections(request):
    category= Category.objects.filter(status=0)
    return render(request, 'shop/collections.html', context={
        "category":category
    })

def collectionsview(request,name):
    if(Category.objects.filter(name=name , status=0)):
            products = Product.objects.filter(category__name=name)
            return render(request, 'shop/products/index.html', context={
        "products":products,
        "category_name":name
    })
    else:
         messages.warning(request,' No Such Category Found')
         return redirect ('collections')
    
def Product_detail(request,cname,pname):
    if (Category.objects.filter(name=cname , status=0)):
        if (Product.objects.filter(name=pname , status=0)):
            products=Product.objects.filter(name=pname).first()
            return render(request,'shop/products/product_details.html',context={'products':products})
        else:
            messages.error(request,'no such product found')
            return redirect('collections')
    else:
        messages.error(request,'no such category found')
        return redirect('collections')
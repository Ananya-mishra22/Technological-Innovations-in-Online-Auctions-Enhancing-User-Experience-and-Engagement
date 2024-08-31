from django.shortcuts import render, HttpResponse , redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    user=request.user
    print(user)
    if user.is_authenticated:
        return render(request , 'home.html')
    
def index(request):
    return render(request, 'ooa.html')
    
def signup(request):
    if request.method =='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Your password and confrim password are not Same!!")
        else:
            my_user=User.objects.create_user(uname,email,pass1)
            return redirect('signin')
    return render(request,'signup.html')

def signin(request):
    if request.method =='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        print(username,password)
        user=authenticate(username=username, password=password)
        print(username,password)
        print(user)
        if user is not None:
            login(request,user)
            return redirect('Home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'Signin.html')


def user_logout(request):
    logout(request)
    return redirect('index')
# Create your views here.

@login_required
def contact(request):
    user=request.user
    print(user)
    if user.is_authenticated:
        return render(request,'contact.html')
    
@login_required
def item(request):
    user=request.user
    if user.is_authenticated:
        return render(request,'item.html')


def item1(request):
    return render(request,'item1.html')
from django.contrib import admin
from django.urls import path
from Home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/",views.home,name='Home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='index'),
    path('viewitem/', views.item1, name='viewitem'),
    path('item/', views.item, name='item'),
    path('logout/', views.user_logout, name='logout'),
]

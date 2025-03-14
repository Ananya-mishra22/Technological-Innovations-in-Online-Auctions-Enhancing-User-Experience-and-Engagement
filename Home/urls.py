from django.contrib import admin
from django.urls import path
from Home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/",views.home,name='Home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
     path('/base', views.base_view, name='base'),  # Route to the base view
    path('', views.index, name='index'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/', views.profile_view, name='profile'),
    # path('viewitem/', views.item1, name='viewitem'),
    path('item/<int:product_id>/', views.item, name='item'),
    path('categoryitems/<str:category>/', views.categoryitems, name='categoryitems'),
    path('register/<int:product_id>/', views.auction_registration, name='auction_registration'),
    path('contact/', views.contact_us, name='contact_us'),
    path('orders/', views.orders, name='orders'),
    path('events/', views.events, name='events'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('bid_now/<int:product_id>/', views.bid_now, name='bid_now'),
    path('search/', views.product_search, name='product_search'),
    path('close-auction/<int:product_id>/', views.close_auction_view, name='close_auction'),
    path('remove_registration/<int:product_id>/', views.remove_registration, name='remove_registration'),
    path('logout/', views.user_logout, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
]

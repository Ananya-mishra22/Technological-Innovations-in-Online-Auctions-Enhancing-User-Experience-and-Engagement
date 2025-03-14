from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image_url = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# ProductAttribute model
class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute_name = models.CharField(max_length=255)
    attribute_value = models.TextField()

    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"
    
# Auction model
class Auction(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='auction')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Auction for {self.product.name}: {self.start_date} to {self.end_date}"

    @property
    def is_active(self):
        """
        Returns True if the auction is currently active.
        """
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        """
        Returns True if the auction is scheduled for the future.
        """
        now = timezone.now()
        return self.start_date > now
    @property
    def has_ended(self):
        now = timezone.now()
        return now > self.end_date
    
    
class AuctionRegistration(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to the Product model
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)  # Adjust the max_length as needed
    address = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return f"{self.username.username} - {self.product.name}"
class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    file = models.FileField(upload_to='contact_files/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"
    

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"
    

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bid_amount}"
    
    
class WinningBid(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)  # Link to the winning bid
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who won the bid
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)  # Link to the auction
    won_at = models.DateTimeField(auto_now_add=True)  # Time when the bid was won

    def __str__(self):
        return f"{self.user.username} won {self.auction.product.name} with bid {self.bid.bid_amount}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

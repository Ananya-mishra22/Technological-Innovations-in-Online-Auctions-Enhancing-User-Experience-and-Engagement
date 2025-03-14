# context_processors.py
from .models import Product

def product_context(request):
    # Fetch all products
    products = Product.objects.all()

    # Initialize won_products as an empty queryset
    won_products = Product.objects.none()

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch products that the user won via WinningBid model
        won_products = Product.objects.filter(auction__winningbid__user=request.user)

    return {
        'products': products,
        'won_products': won_products,
    }

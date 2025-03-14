from django.shortcuts import render, HttpResponse , redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import  HttpResponseForbidden
from .models import Product,ProductAttribute,Category, Auction, AuctionRegistration, ContactUs, WishlistItem, Bid, WinningBid, UserProfile
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError  # Import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .tokens import email_verification_token  # Import the token generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str  # Use force_str for Django >= 3.0
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model




def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. You can now login your account.")
        return redirect('signin')
    else:
        messages.error(request, "Activation link is invalid!")
        return render(request, 'activation_invalid.html')




def product_search(request):
    user=request.user
    if user.is_authenticated:
        query = request.GET.get('q')  # Fetch the search query from the request
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if query:
            # Search in 'name' and 'description' fields
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            products = Product.objects.all()  # If no search query, return all products

        context = {
            'products': products,
        }
        
        return render(request, 'product_search_results.html', context)
    else:
        query = request.GET.get('q')  # Fetch the search query from the request
        
        if query:
            # Search in 'name' and 'description' fields
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            products = Product.objects.all()  # If no search query, return all products

        context = {
            'products': products,
            'profile':profile,
        }
        
        return render(request, 'product_search_results copy.html', context)


@login_required
def home(request):
    user=request.user
    print(user)
    if user.is_authenticated:
        """
        Renders the home page with upcoming and active auctions.
        """
        products = Product.objects.all()

        wishlist_product_ids = set()
        
        if request.user.is_authenticated:
            # Fetch all product IDs in the user's wishlist
            profile = UserProfile.objects.filter(user=request.user)
            wishlist_product_ids = set(
                WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
            )
        # Annotate each product with 'in_wishlist' attribute
        for product in products:
            product.in_wishlist = product.id in wishlist_product_ids


        now = timezone.now()

        # Fetch products with auctions that are either active or upcoming
        upcoming_auctions = Product.objects.filter(
            auction__end_date__gte=now
        ).order_by('auction__start_date')  # Orders by start date ascending

        
        context = {
            'upcoming_auctions': upcoming_auctions,
            'user':user,
            'products': products,
            'wishlist_product_ids': wishlist_product_ids,
            'profile':profile,
        }
        return render(request , 'home.html', context)
    
def index(request):
        """
        Renders the home page with upcoming and active auctions.
        """
        products = Product.objects.all()

        wishlist_product_ids = set()

        if request.user.is_authenticated:
            # Fetch all product IDs in the user's wishlist
            wishlist_product_ids = set(
                WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
            )
        # Annotate each product with 'in_wishlist' attribute
        for product in products:
            product.in_wishlist = product.id in wishlist_product_ids


        now = timezone.now()

        # Fetch products with auctions that are either active or upcoming
        upcoming_auctions = Product.objects.filter(
            auction__end_date__gte=now
        ).order_by('auction__start_date')  # Orders by start date ascending

        context = {
            'upcoming_auctions': upcoming_auctions,
            'products': products,
            'wishlist_product_ids': wishlist_product_ids,
        }
        return render(request, 'ooa.html',context)
    
from django.core.mail import EmailMessage

def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            messages.error(request, "Your password and confirm password are not the same!")
            return render(request, 'signup.html')
        elif not validate_password(pass1):
            messages.error(request, "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
            return render(request, 'signup.html')
        else:
            user = User.objects.create_user(uname, email, pass1)
            user.is_active = False  # Deactivate account until it is confirmed
            user.save()

            # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_verification_token.make_token(user),
            })
            to_email = email
            email_message = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email_message.send()

            messages.success(request, "Registration successful! Please check your email to activate your account.")
            return redirect('signin')
    return render(request, 'signup.html')

def validate_password(password):
    # Check password length
    if len(password) < 8:
        return False
    
    # Check for uppercase, lowercase, digit, and special character
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in '!@#$%^&*()-_=+[]{};:,.<>?/' for char in password):
        return False
    
    return True

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


def base_view(request):
    user=request.user
    products = Product.objects.all()  # Fetch all products
    
   # Initialize won_products as an empty queryset
    won_products = Product.objects.none()
    
    

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch products that the user won via WinningBid model
        profile = UserProfile.objects.filter(user=request.user)
        won_products = Product.objects.filter(auction__winningbid__user=request.user)
    
    

    context = {
        'products': products,  # Pass the products to the template
        'won_products': won_products,  # Add won products to context
        'profile':profile,
    }
    return render(request, 'index1.html', context)

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
    

def item(request,product_id):
    user=request.user
    if user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        print(product.name)
        in_wishlist = False  # Default value

        if request.user.is_authenticated:
            in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()# Check if the product is in the user's wishlist

        attributes = ProductAttribute.objects.filter(product=product) # Fetch product attributes
        similarproducts= Product.objects.filter(category=product.category).exclude(id=product.id) #similar products
        try:
            auction = product.auction  # Access the related Auction via related_name
        except Auction.DoesNotExist:
            auction = None

        context = {
            'product': product, 'attributes': attributes, 'similarproducts':similarproducts, 'auction': auction, 'in_wishlist': in_wishlist,
        }
        return render(request,'item.html', context)
    else:
        product = get_object_or_404(Product, id=product_id)
        print(product.name)
        in_wishlist = False  # Default value

        if request.user.is_authenticated:
            in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists() # Check if the product is in the user's wishlist

        attributes = ProductAttribute.objects.filter(product=product) # Fetch product attributes
        similarproducts= Product.objects.filter(category=product.category).exclude(id=product.id) #similar products
        try:
            auction = product.auction  # Access the related Auction via related_name
        except Auction.DoesNotExist:
            auction = None

        context = {
            'product': product, 'attributes': attributes, 'similarproducts':similarproducts, 'auction': auction, 'in_wishlist': in_wishlist,
        }

        return render(request,'item1.html', context)
    

def categoryitems(request, category):
    user=request.user
    print(category)
    if user.is_authenticated:
        category = get_object_or_404(Category, name=category)
        # category = Category.objects.filter(name=category).last()
        print(category)
        products = Product.objects.filter(category=category).order_by('-id')
        context = {
            'category': category,
            'products': products
        }
        return render(request,'catagoreyitems.html', context)
    else:
        category = get_object_or_404(Category, name=category)
        # category = Category.objects.filter(name=category).last()
        print(category)
        products = Product.objects.filter(category=category).order_by('-id')
        context = {
            'category': category,
            'products': products
        }
        return render(request,'catagoreyitembefore.html', context)
    


@login_required
def orders(request):
    user=request.user
    if user.is_authenticated:
        # Fetch auction registrations for the current user
        auction_registrations = AuctionRegistration.objects.filter(username=request.user)

        # Get the related products from the auction registrations
        products = Product.objects.filter(id__in=auction_registrations.values_list('product_id', flat=True))
         
        # Fetch items that the user won (add your own logic to track this, e.g., via a 'won' flag in Auction or Product model) 
        won_products = Product.objects.filter(auction__winningbid__user=request.user)


        context = {
            'auction_registrations': auction_registrations,
            'products': products,
            'won_products': won_products,  # Add won products to context
        }
        return render(request, 'orders.html', context)

@login_required
def remove_registration(request, product_id):
    # Remove the auction registration
    AuctionRegistration.objects.filter(username=request.user, product_id=product_id).delete()
    return redirect('orders')


# @login_required
# def bid_now(request, product_id):
#     """
#     Adds a product to the authenticated user's wishlist.
#     """
#     product = get_object_or_404(Product, id=product_id)
#     wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
#     if created:
#         messages.success(request, f"Added '{product.name}' to your wishlist.")
#     else:
#         messages.info(request, f"'{product.name}' is already in your wishlist.")
#     return redirect('item', product_id=product.id)  # Replace 'product_detail' with your actual product detail view name


@login_required
def wishlist(request):
    user=request.user
    if user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
        return render(request,'wishlist.html', {'wishlist_items': wishlist_items})
    

def events(request):
    user=request.user
    if user.is_authenticated:
        return render(request,'events.html')
    else:
        return render(request,'event.html')
 
@login_required
def auction_registration(request, product_id):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('fullName')
        phone_number = request.POST.get('phone')
        address = request.POST.get('address')

        # Email content
        full_message = f"Name: {full_name}\nEmail: {email}\nPhone: {phone_number}\nAddress: {address}"
        
        # Send email to admin
        send_mail(
            subject=f'New Auction Registration from {full_name}',
            message=full_message,
            from_email=email,
            recipient_list=[email],  # Replace with admin email
        )
        
        # Check if the user with the provided username exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse("Username does not exist!")
        
        product = get_object_or_404(Product, id=product_id)# Fetch the product associated with the registration

        # Ensure email matches the one in the user profile for extra security
        if user.email != email:
            return HttpResponse("Email does not match the user's email!")

        # Create the auction registration for the authenticated user
        AuctionRegistration.objects.create(
            username=user,  # Save the actual user instance
            product=product,
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            address=address
        )

        # Redirect to a success page after successful registration
        return redirect("Home")  # Define a success URL

    # Render the registration form if the request is not POST
    return render(request, 'Registerforauction.html')
    #     return HttpResponseRedirect(request.path_info)  # Redirect to a success page
    # # Return JSON response
    #     return JsonResponse({'message': 'Thank you for your Response. We will contact you soon!'})


    # return render(request, 'Registerforauction.html')  # Render the form if not POST

    #     return redirect('auction_registration')  # Redirect to a success page or the auction page

    # return render(request, 'Registerforauction.html') 


def contact_us(request):
    user=request.user
    if user.is_authenticated:
        if request.method == 'POST':
            # Extract form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            file = request.FILES.get('file')

            # Initialize a flag to track form validity
            form_is_valid = True

            # Validate required fields
            if not name:
                messages.error(request, "Name is required.")
                form_is_valid = False

            if not email:
                messages.error(request, "Email is required.")
                form_is_valid = False
            else:
                # Validate email format
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, "Enter a valid email address.")
                    form_is_valid = False

            if not subject:
                messages.error(request, "Subject is required.")
                form_is_valid = False

            if not message:
                messages.error(request, "Message is required.")
                form_is_valid = False

            # Optional: Validate file type and size
            if file:
                # Example: Restrict to certain file types (e.g., PDF, DOCX, PNG, JPG)
                allowed_content_types = ['application/pdf', 'application/msword',
                                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                        'image/jpeg', 'image/png']
                if file.content_type not in allowed_content_types:
                    messages.error(request, "Unsupported file type.")
                    form_is_valid = False

                # Example: Restrict file size to 5MB
                if file.size > 5 * 1024 * 1024:
                    messages.error(request, "File size should not exceed 5MB.")
                    form_is_valid = False

            if form_is_valid:
                # Save the contact message
                ContactUs.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    file=file
                )

                messages.success(request, "Your message has been sent successfully!")
                return redirect('contact_us')  # Replace with your desired redirect URL name

            else:
                # If the form is invalid, redirect back with error messages
                return redirect('contact_us')

        else:
            # GET request: Display the contact form
            return render(request, 'contactus.html')
    else:
        if request.method == 'POST':
            # Extract form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            file = request.FILES.get('file')

            # Initialize a flag to track form validity
            form_is_valid = True

            # Validate required fields
            if not name:
                messages.error(request, "Name is required.")
                form_is_valid = False

            if not email:
                messages.error(request, "Email is required.")
                form_is_valid = False
            else:
                # Validate email format
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, "Enter a valid email address.")
                    form_is_valid = False

            if not subject:
                messages.error(request, "Subject is required.")
                form_is_valid = False

            if not message:
                messages.error(request, "Message is required.")
                form_is_valid = False

            # Optional: Validate file type and size
            if file:
                # Example: Restrict to certain file types (e.g., PDF, DOCX, PNG, JPG)
                allowed_content_types = ['application/pdf', 'application/msword',
                                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                        'image/jpeg', 'image/png']
                if file.content_type not in allowed_content_types:
                    messages.error(request, "Unsupported file type.")
                    form_is_valid = False

                # Example: Restrict file size to 5MB
                if file.size > 5 * 1024 * 1024:
                    messages.error(request, "File size should not exceed 5MB.")
                    form_is_valid = False

            if form_is_valid:
                # Save the contact message
                ContactUs.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    file=file
                )

                messages.success(request, "Your message has been sent successfully!")
                return redirect('contact_us')  # Replace with your desired redirect URL name

            else:
                # If the form is invalid, redirect back with error messages
                return redirect('contact_us')

        else:
            # GET request: Display the contact form
            return render(request, 'contactus copy.html')
    
    
@login_required
def add_to_wishlist(request, product_id):
    """
    Adds a product to the authenticated user's wishlist.
    """
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"Added '{product.name}' to your wishlist.")
    else:
        messages.info(request, f"'{product.name}' is already in your wishlist.")
    return redirect('item', product_id=product.id)  # Replace 'product_detail' with your actual product detail view name


@login_required
def remove_from_wishlist(request, product_id):
    """
    Removes a product from the authenticated user's wishlist.
    """
    product = get_object_or_404(Product, id=product_id)
    try:
        wishlist_item = WishlistItem.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f"Removed '{product.name}' from your wishlist.")
    except WishlistItem.DoesNotExist:
        messages.info(request, f"'{product.name}' was not in your wishlist.")
    return redirect('wishlist')  # Replace 'wishlist' with your actual wishlist view name

@login_required
def bid_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    auction = product.auction

    # Check if the auction is active
    if not auction.is_active:
        return redirect('close_auction', product_id=product.id)
    
    # Check if the user is registered for the auction
    if not AuctionRegistration.objects.filter(username=request.user, product=product).exists():
        return HttpResponseForbidden("You are not registered for this auction.")

    # Get the current highest bid
    highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_amount').first()

    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        
        # Ensure bid_amount is higher than the current highest bid
        if highest_bid and float(bid_amount) <= highest_bid.bid_amount:
            return HttpResponse("Your bid must be higher than the current highest bid.")

        # Create the new bid
        Bid.objects.create(auction=auction, user=request.user, bid_amount=bid_amount)

        return redirect('bid_now', product_id=product.id)

    context = {
        'product': product,
        'highest_bid': highest_bid,
        'auction': auction,
    }
    return render(request, 'bid_now.html', context)


def close_auction(product_id):
    product = get_object_or_404(Product, id=product_id)
    auction = product.auction
    #auction = Auction.objects.get(id=auction_id)
    if auction.is_active:  # Check if the auction is active
        return "Auction is still active."

    # Get the highest bid for the auction
    highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_amount').first()
    
    
    if highest_bid:
        # Assign the highest bid amount to the product's price
        auction.product.price = highest_bid.bid_amount  # Correctly assign bid_amount (DecimalField)
        auction.product.save()  # Save the product with updated price

    if highest_bid:
        # Create a WinningBid instance
        WinningBid.objects.create(
            bid=highest_bid,
            user=highest_bid.user,
            auction=auction
        )
        return f"{highest_bid.user.username} has won the auction for {auction.product.name} with a bid of {highest_bid.bid_amount}."
    else:
        return "No bids were placed for this auction."
    
@login_required
def close_auction_view(request, product_id):
    result = close_auction(product_id)  # Call the task

    # Add the result as a message
    messages.info(request, result)

    # Redirect back to the orders page or wherever appropriate
    return redirect('orders')  # Replace with your desired URL name



@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        bio = request.POST.get('bio', '')

        # Update user fields
        request.user.username = username
        request.user.email = email
        request.user.save()

        # Update profile picture and bio
        user_profile.bio = bio
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()

        return redirect('profile')  # Replace with the name of the profile view

    context = {
        'user_profile': user_profile,
    }

    return render(request, 'edit_profile.html', context)

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


def checkout(request):
    # Fetch items that the user won (add your own logic to track this, e.g., via a 'won' flag in Auction or Product model) 
    won_products = Product.objects.filter(auction__winningbid__user=request.user)
    context = {
        'won_products': won_products,
    }
    return render(request, 'Checkout.html',context)
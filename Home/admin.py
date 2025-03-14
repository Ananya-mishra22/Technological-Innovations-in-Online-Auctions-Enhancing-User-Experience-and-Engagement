from django.contrib import admin
from Home.models import Category, Product, ProductAttribute,Auction, AuctionRegistration, ContactUs, WishlistItem, Bid, WinningBid

# Register your models here.
# Define inline admins for related objects
class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ('user', 'bid_amount', 'timestamp')
    can_delete = False
    verbose_name = "Bid"
    verbose_name_plural = "Bids"

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductAttribute)
admin.site.register(AuctionRegistration)

@admin.register(WinningBid)
class WinningBidAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'auction', 'bid', 'won_at')
    search_fields = ('user__username', 'auction__product__name', 'bid__bid_amount')
    list_filter = ('won_at',)
    readonly_fields = ('id', 'won_at')

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('product__name',)
    readonly_fields = ('id', 'is_active')
    
    # Display related bids inline
    inlines = [BidInline]  # Correctly adds the BidInline here
    
    
@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('submitted_at',)


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'added_on')
    list_filter = ('user', 'added_on')
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_on',)
    

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'user', 'bid_amount', 'timestamp')
    search_fields = ('auction__product__name', 'user__username')
    list_filter = ('timestamp', 'bid_amount')
    readonly_fields = ('id', 'timestamp')


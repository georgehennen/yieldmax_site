from django.contrib import admin
from .models import UserProfile, Lot 
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nlv_goal', 'monthly_goal', 'nav_goal', 'marginal_tax_rate', 'current_margin_used', 'margin_interest_rate') # Added new field
    search_fields = ('user__username',)
@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'date_purchased', 'shares', 'price')
    list_filter = ('user', 'ticker', 'date_purchased')
    search_fields = ('user__username', 'ticker')
from django.contrib import admin
from .models import ETF

@admin.register(ETF)
class ETFAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'underlying_asset', 'strategy', 'dividend_frequency', 'current_price', 'annual_yield_percentage', 'last_updated')
    list_filter = ('strategy', 'dividend_frequency')
    search_fields = ('ticker', 'underlying_asset')

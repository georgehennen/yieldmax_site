from django.contrib import admin
from .models import ETF, ExDividendRecord

@admin.register(ETF)
class ETFAdmin(admin.ModelAdmin):
    list_display = (
        'ticker',
        'underlying_asset',
        'strategy',
        'description',
        'fund_issuer',
        'get_dividend_frequency',
        'current_price',
        'annual_yield_percentage',
        'last_updated',
    )
    list_filter = ('strategy', 'description', 'fund_issuer')
    search_fields = ('ticker', 'underlying_asset')

    def get_dividend_frequency(self, obj):
        return obj.days_between_last_ex_dates()
    get_dividend_frequency.short_description = 'Dividend Freq (days)'

@admin.register(ExDividendRecord)
class ExDividendRecordAdmin(admin.ModelAdmin):
    list_display = ('etf', 'ex_date')
    list_filter = ('etf',)
    search_fields = ('etf__ticker',)

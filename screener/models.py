from django.db import models
from decimal import Decimal

class ETF(models.Model):
    # --- Static Data ---
    ticker = models.CharField(max_length=10, unique=True, primary_key=True)
    underlying_asset = models.CharField(max_length=20, help_text="e.g., TSLA, NVDA, QQQ")
    class Strategy(models.TextChoices):
        BULLISH = 'Bullish', 'Bullish'
        BEARISH = 'Bearish', 'Bearish'
    strategy = models.CharField(max_length=20, choices=Strategy.choices)
    class Frequency(models.TextChoices):
        WEEKLY = 'Weekly', 'Weekly'
        MONTHLY = 'Monthly', 'Monthly'
    dividend_frequency = models.CharField(max_length=10, choices=Frequency.choices)
    
    # --- Fields for Cached/Fetched Dynamic Data ---
    # These fields can be populated by a periodic task to speed up the app.
    # For now, the view will fetch them live.
    last_updated = models.DateTimeField(auto_now=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    annual_yield_percentage = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    price_vs_lower_median_percentage = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    next_ex_dividend_date = models.DateField(null=True, blank=True)
    underlying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    underlying_target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    underlying_percent_from_6m_high = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    underlying_percent_to_target = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    def __str__(self):
        return self.ticker

    class Meta:
        ordering = ['ticker']
        verbose_name = "ETF"
        verbose_name_plural = "ETFs"

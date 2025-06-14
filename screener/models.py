from django.db import models
from decimal import Decimal
from datetime import timedelta

class ETF(models.Model):
    # --- Static Data ---
    ticker = models.CharField(max_length=10, unique=True, primary_key=True)
    underlying_asset = models.CharField(max_length=20, help_text="e.g., TSLA, NVDA, QQQ")
    class Strategy(models.TextChoices):
        BULLISH = 'Bullish', 'Bullish'
        BULLISH_LEVERAGED = 'Bullish Leveraged', 'Bullish Leveraged'
        BEARISH = 'Bearish', 'Bearish'

    strategy = models.CharField(max_length=20, choices=Strategy.choices)

    class Description(models.TextChoices):
        SYNTHETIC_COVERED_CALL = 'Synthetic Covered Call (Call-Write)', 'Synthetic Covered Call (Call-Write)'
        COVERED_CALL = 'Covered Call (Call-Write)', 'Covered Call (Call-Write)'
        LEVERAGE = 'Leverage', 'Leverage'
        PUT_WRITE = 'Put-Write', 'Put-Write'
        PUT_BUY_WRITE = 'Put-Buy/Write', 'Put-Buy/Write'
        CREDIT_CALL_SPREADS = 'Credit Call Spreads', 'Credit Call Spreads'
        SYNTHETIC_COVERED_PUT = 'Synthetic Covered Put (Put-Write)', 'Synthetic Covered Put (Put-Write)'

    description = models.CharField(max_length=50, choices=Description.choices)

    class FundIssuer(models.TextChoices):
        YIELDMAX = 'YieldMax', 'YieldMax'
        ROUNDHILL = 'Roundhill', 'Roundhill'
        GRANITESHARES = 'GraniteShares', 'GraniteShares'
        REXSHARES = 'RexShares', 'RexShares'
        KURV = 'Kurv', 'Kurv'
        DEFIANCE = 'Defiance', 'Defiance'

    fund_issuer = models.CharField(
        max_length=50,
        choices=FundIssuer.choices,
        default=FundIssuer.YIELDMAX
    )

    last_updated = models.DateTimeField(auto_now=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    annual_yield_percentage = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    price_vs_lower_median_percentage = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    next_ex_dividend_date = models.DateField(null=True, blank=True)
    underlying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    underlying_target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    underlying_percent_from_6m_high = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    underlying_percent_to_target = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)

    def days_between_last_ex_dates(self):
        records = self.ex_dividends.all()[:2]  # Get the two most recent ex-dates
        if len(records) == 2:
            return (records[0].ex_date - records[1].ex_date).days
        return None  # Not enough data
    
    def __str__(self):
        return self.ticker

    class Meta:
        ordering = ['ticker']
        verbose_name = "ETF"
        verbose_name_plural = "ETFs"
        indexes = [
            models.Index(fields=['ticker']),
            models.Index(fields=['underlying_asset']),
        ]

class ExDividendRecord(models.Model):
    etf = models.ForeignKey(ETF, related_name='ex_dividends', on_delete=models.CASCADE)
    ex_date = models.DateField()
    class Meta:
        ordering = ['-ex_date']  # Ensures latest comes first

    def __str__(self):
        return f"{self.etf.ticker} - {self.ex_date}"


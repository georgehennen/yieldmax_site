from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nlv_goal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('250000.00'), null=True, blank=True) 
    monthly_goal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('12000.00'), null=True, blank=True)
    nav_goal = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'), null=True, blank=True) 
    marginal_tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.3700'), null=True, blank=True) 
    current_margin_used = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    margin_interest_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0700'), null=True, blank=True) # New field, e.g., 0.07 for 7% APR

    def __str__(self): return f"{self.user.username}'s Profile"

class Lot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lots")
    ticker = models.CharField(max_length=10)
    date_purchased = models.DateField()
    shares = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs): self.ticker = self.ticker.upper(); super().save(*args, **kwargs)
    def __str__(self): return f"{self.ticker} - {self.shares} shares @ ${self.price} on {self.date_purchased}"
    class Meta: ordering = ["-date_purchased"]
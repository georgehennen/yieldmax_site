from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Lot 
from decimal import Decimal

# NEW - The registration form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email Address'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

class GoalForm(forms.ModelForm):
    nav_goal_percentage = forms.DecimalField(label="NAV Goal (%)", max_digits=5, decimal_places=2, help_text="Enter as a number, e.g., 5 for 5%.", required=False)
    class Meta: model = UserProfile; fields = ["nlv_goal", "monthly_goal"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-sm'})
            if field_name == 'nlv_goal': field.label = "NLV Goal ($)"; field.widget.attrs.update({'placeholder': 'e.g., 250000.00'})
            elif field_name == 'monthly_goal': field.label = "Monthly Income Goal ($)"; field.widget.attrs.update({'placeholder': 'e.g., 12000.00'})
        if self.instance and self.instance.pk and self.instance.nav_goal is not None: 
            self.fields['nav_goal_percentage'].initial = (self.instance.nav_goal * Decimal(100)).quantize(Decimal('0.01'))
        self.fields['nav_goal_percentage'].widget.attrs.update({'class': 'form-control form-control-sm'})
    def save(self, commit=True):
        instance = super().save(commit=False)
        nav_goal_perc = self.cleaned_data.get('nav_goal_percentage')
        instance.nav_goal = nav_goal_perc / Decimal(100) if nav_goal_perc is not None else None
        if commit: instance.save()
        return instance

class FinancialSettingsForm(forms.ModelForm):
    marginal_tax_rate_percentage = forms.DecimalField(label="Marginal Tax Rate (%)", max_digits=5, decimal_places=2, help_text="Enter as a number, e.g., 32 for 32%.", required=False)
    margin_interest_rate_percentage = forms.DecimalField(label="Margin Annual Interest Rate (%)", max_digits=5, decimal_places=2, help_text="Enter as a number, e.g., 7 for 7%.", required=False) 
    class Meta: model = UserProfile; fields = ["current_margin_used"] 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_margin_used'].label = "Current Margin Used ($)"
        self.fields['current_margin_used'].widget.attrs.update({'class': 'form-control form-control-sm', 'placeholder': 'e.g., 5000.00'})
        if self.instance and self.instance.pk:
            if self.instance.marginal_tax_rate is not None: self.fields['marginal_tax_rate_percentage'].initial = (self.instance.marginal_tax_rate * Decimal(100)).quantize(Decimal('0.01'))
            if self.instance.margin_interest_rate is not None: self.fields['margin_interest_rate_percentage'].initial = (self.instance.margin_interest_rate * Decimal(100)).quantize(Decimal('0.01'))
        self.fields['marginal_tax_rate_percentage'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['margin_interest_rate_percentage'].widget.attrs.update({'class': 'form-control form-control-sm'}) 
    def save(self, commit=True):
        instance = super().save(commit=False) 
        tax_rate_perc = self.cleaned_data.get('marginal_tax_rate_percentage')
        instance.marginal_tax_rate = tax_rate_perc / Decimal(100) if tax_rate_perc is not None else None
        margin_interest_perc = self.cleaned_data.get('margin_interest_rate_percentage') 
        instance.margin_interest_rate = margin_interest_perc / Decimal(100) if margin_interest_perc is not None else None 
        if commit: instance.save()
        return instance

class LotForm(forms.ModelForm):
    class Meta: model = Lot; fields = ["ticker", "date_purchased", "shares", "price"]; widgets = {"date_purchased": forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'date_purchased': field.widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['ticker'].widget.attrs.update({'placeholder': 'e.g. TSLY'})
        self.fields['shares'].widget.attrs.update({'placeholder': 'e.g. 100.50'})
        self.fields['price'].widget.attrs.update({'placeholder': 'e.g. 15.75'})
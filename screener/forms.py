from django import forms
from .models import ETF

class ScreenerFilterForm(forms.Form):
    # Updated to match the fields shown in the screenshot and user intent
    strategy = forms.MultipleChoiceField(
        choices=ETF.Strategy.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=[ETF.Strategy.BULLISH, ETF.Strategy.BEARISH]
    )
    
    dividend_frequency = forms.ChoiceField(
        choices=[('All', 'All')] + ETF.Frequency.choices,
        required=False,
        initial='All'
    )
    
    min_yield = forms.FloatField(
        label="Min Annual Yield (%)",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 70'})
    )
    
    max_pvlm = forms.FloatField(
        label="Max Price vs. Lower Median (%)",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., -5'})
    )

    max_from_6m_high = forms.FloatField(
        label="Max Underlying % from 6M High",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., -10'})
    )
    
    min_to_target = forms.FloatField(
        label="Min Underlying % to Target",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 10'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control form-control-sm'})

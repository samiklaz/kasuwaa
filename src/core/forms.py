from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('Stripe', 'Stripe'),
    ('Paypal', 'Paypal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your address',
        'class': 'form-control col-md-10'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your address',
        'class': 'form-control col-md-10'
    }))
    country = CountryField(blank_label='Select Country').formfield(widget=CountrySelectWidget(attrs={
        'class': 'form-control col-md-10'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your address',
        'class': 'form-control col-md-10'
    }))
    # same_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    # save_info = forms.BooleanField(widget=forms.CheckboxInput())
    # payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField()
    email = forms.EmailField()
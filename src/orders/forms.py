from django import forms
from django.contrib.auth import get_user_model

from orders.models import UserCheckout
from .models import UserAddress

User = get_user_model()
class GuestCheckoutForm(forms.Form):
    email = forms.EmailField()
    email_confirmation = forms.EmailField(label="Verify Email")

    # Don't call clean_email. Set the last email_confirmation
    def clean_email_confirmation(self):
        email = self.cleaned_data.get("email")
        email_confirmation = self.cleaned_data.get("email_confirmation")

        if email == email_confirmation:
            user_exists = UserCheckout.objects.filter(email=email).count()
            print(user_exists)
            if user_exists !=0:
                raise forms.ValidationError("The Email already exists, please log in to continue")
            return email_confirmation
        else:
            raise forms.ValidationError("Please confirm emails are the same")

class AddressForm(forms.Form):
    billing_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="billing"),
        empty_label=None,
        widget=forms.RadioSelect
    )
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="shipping"),
        empty_label=None,
        widget=forms.RadioSelect
    )

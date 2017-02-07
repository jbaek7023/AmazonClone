from django.shortcuts import render
from django.views.generic import FormView

from .forms import AddressForm
from .models import UserAddress


# Create your views here.
class AddressSelectFormView(FormView):
    form_class = AddressForm
    template_name = "orders/address_select.html"

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        # print(form.fields)
        try:
            form.fields["billing_address"].queryset = UserAddress.objects.filter(
                user__email = self.request.user.email,
                type = 'billing'
            )
            form.fields["shipping_address"].queryset = UserAddress.objects.filter(
                user__email=self.request.user.email,
                type='shipping'
            )
        except:
            #if not authenticated, cause error
            pass

        return form

    def form_valid(self, form, *args, **kwargs):
        self.request.session["shipping_address_id"] = form.cleaned_data["shipping_address"].id
        self.request.session["billing_address_id"] = form.cleaned_data["billing_address"].id
        # print(form.cleaned_data["shipping_address"])
        # print(form.cleaned_data["billing_address"])

        form = super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)
        return form

    def get_success_url(self, *args, **kwargs):
        return "/checkout/"

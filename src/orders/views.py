from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView

from .forms import AddressForm, UserCheckout, UserAddressForm
from .models import UserAddress, Order
from .mixins import CartOrderMixin, LoginRequiredMixin
# implement LoginRequiredMixin in Accounts app next time.

class OrderDetail(DetailView):
    model = Order #obj is model as well

    def dispatch(self, request, *args, **kwargs):
        try:
            user_checkout_id = self.request.session.get("user_checkout_id")
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        except UserCheckout.DoesNotExist:
            user_checkout = UserCheckout.objects.get(user=request.user)
        except:
            user_checkout = None

        obj = self.get_object()
        if obj.user == user_checkout and user_checkout is not None:
            return super(OrderDetail, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class OrderList(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()

    def get_queryset(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return super(OrderList, self).get_queryset().filter(user=user_checkout)

class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = "forms.html"
    success_url = "/checkout/address/"

    def get_checkout_user(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return user_checkout

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.get_checkout_user()
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

# Create your views here.
class AddressSelectFormView(CartOrderMixin, FormView):
    form_class = AddressForm
    template_name = "orders/address_select.html"

    def dispatch(self, *args, **kwargs):
        b_address, s_address = self.get_address()
        if b_address.count() == 0 :
            messages.success(self.request, "Please add a billing address before continuing ")
            return redirect("user_create_address")
        elif s_address.count() ==0:
            messages.success(self.request, "Please add a shipping address before continuing ")
            return redirect("user_create_address")
        else:
            return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

    def get_address(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)

        b_address = UserAddress.objects.filter(
            # user__email = self.request.user.email,
            user=user_checkout,
            type='billing'
        )

        s_address = UserAddress.objects.filter(
            # user__email = self.request.user.email
            user=user_checkout,
            type='shipping'
        )
        return b_address, s_address


    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        # print(form.fields)

        b_address, s_address = self.get_address()

        form.fields["billing_address"].queryset = b_address
        form.fields["shipping_address"].queryset = s_address
        return form

    def form_valid(self, form, *args, **kwargs):
        shipping_address = form.cleaned_data["shipping_address"]
        billing_address= form.cleaned_data["billing_address"]

        order = self.get_order()
        order.shipping_address = shipping_address
        order.billing_address = billing_address
        order.save()

        form = super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)
        return form

    def get_success_url(self, *args, **kwargs):
        return "/checkout/"

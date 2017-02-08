from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic import View
from  django.views.generic.list import ListView

# Create your views here.
from orders.forms import GuestCheckoutForm
from orders.models import UserCheckout, Order, UserAddress
from products.models import Variation
from carts.models import Cart, CartItem
from orders.mixins import CartOrderMixin
from django.views.generic.edit import FormMixin


class ItemCountView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id == None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            request.session["cart_item_count"] = count
            return JsonResponse({"count":count})

        else:
            raise Http404

class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = "carts/view.html"

    # just refactored by no meaning
    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry(0)  # 1800 seconds = 1800.
        cart_id = self.request.session.get("cart_id")

        # if session doesn't have Cart, create the Cart AND set the session [ "cart_id" ]
        if cart_id == None:
            new_cart = Cart()
            new_cart.save()
            cart_id = new_cart.id
            # = Cart.objects.create()
            self.request.session["cart_id"] = new_cart.id
        # Get the Cart. new Cart or existing Cart
        cart = Cart.objects.get(id=cart_id)

        # if user authenticated, set the user of the cart
        if self.request.user.is_authenticated():
            # cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.user = self.request.user
            cart.save()

        return cart

    def get(self, request, *args, **kwargs):
        #get the cart!
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete")

        #flash message
        flash_message = ""

        #If we GET item_id
        if item_id:
            #Get the Variation instance associated with item_id
            item_instance = get_object_or_404(Variation, id=item_id)

            # Set delete_item is True if quantity is less than 0
            quantity = request.GET.get("qty", 1)
            try:
                if int(quantity) < 1:
                    delete_item = True
            except:
                raise Http404

            # Get the cart item
            cart=self.get_object()
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)


            add_or_not = False
            if created:
                flash_message = "Successfully added to the cart"
                add_or_not = True

            # if int(qty_in_cart_item) < 1 :
            #     delete_item=True;
            #     print("delet!!!")

            if delete_item:
                #delete
                flash_message = "Item removed Successfully"
                cart_item.delete()
                delete_item = True
            else:
                #update
                flash_message = "Quantity has been updated successfully"
                cart_item.quantity = quantity
                cart_item.save()
                delete_item = False

            if not request.is_ajax:
                return HttpResponseRedirect(reverse("carts"))

        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None

            try:
                #get the cart
                subtotal = cart_item.cart.sub_total
            except:
                subtotal = None

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None

            try:
                #get the cart
                to_of_total = cart_item.cart.total
            except:
                to_of_total = None

            quantity_cart_item = request.GET.get("qty", 1)


            data = {
                "deleted": delete_item,
                "item_added": add_or_not,
                "line_total": total,
                "sub_total": subtotal,
                "flash_message" : flash_message,
                "tax_total": tax_total,
                "to_of_total": to_of_total
            }
            return JsonResponse(data)


        #render the variations
        context = {
            "object" : self.get_object()
        }
        template = self.template_name

        return render(request, template, context)



class CheckOutView(CartOrderMixin, FormMixin, DetailView):
    model = Cart
    template_name =  "carts/checkout_view.html"
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):
        cart = self.get_cart()

        # if session doesn't have Cart, create the Cart AND set the session [ "cart_id" ]
        if cart == None:
            return None
        # Get the Cart. new Cart or existing Cart
        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckOutView, self).get_context_data(*args, **kwargs)

        # Get user checkout id
        user_checkout_id = self.request.session.get("user_checkout_id")

        user_can_continue = False

        if self.request.user.is_authenticated():
            user_can_continue=True
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            user_checkout.user = self.request.user
            user_checkout.save()
            self.request.session["user_checkout_id"] = user_checkout.id
        elif not self.request.user.is_authenticated() and user_checkout_id == None:
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()
        else:
            pass

        if user_checkout_id !=None:
            user_can_continue = True

        context["order"] = self.get_order()

        context["user_can_continue"] = user_can_continue
        context["form"] = self.get_form()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user_checkout = UserCheckout.objects.get_or_create(email=email)[0]
            request.session["user_checkout_id"] = user_checkout.id
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('checkout')

    def get(self, request, *args, **kwargs):
        get_data = super(CheckOutView, self).get(request, *args, **kwargs)
        # Create order automatically
        cart = self.get_object()
        if cart == None:
            print("in the loop")
            return redirect("carts")
        new_order = self.get_order()


        user_checkout_id = request.session.get('user_checkout_id')
        if user_checkout_id !=None:
            user_checkout = UserCheckout.objects.get(id = user_checkout_id)

            if new_order.billing_address_id == None or new_order.shipping_address_id == None:
                return redirect("order_address") # redirect to the cart


            new_order.user = user_checkout
            new_order.save()
        #done creating order
        return get_data

class CheckoutFinalView(CartOrderMixin, View):
    def post(self, request, *args, **kwargs):
        order = self.get_order()
        if request.POST.get("payment_token")=="ABC":
            order.mark_completed()
            messages.success(request, "Thank you for your order")

            #clean every session
            del request.session["cart_id"]
            del request.session["order_id"]
        return redirect("order_detail", pk=order.id)

    def get(self, request, *args, **kwargs):
        return redirect("checkout")
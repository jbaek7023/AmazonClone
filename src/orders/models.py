from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save

from carts.models import Cart

# Create your models here.
class UserCheckout(models.Model):
    usr = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) #not required
    email = models.EmailField(unique=True) #required

    #merchant_id
    #

    def __str__(self):
        return self.email


ADDRESS_TYPE = {
    ('billing', 'Billing'), #datain db and display str
    ('shipping', 'Shipping'),
}

class UserAddress(models.Model):
    user = models.ForeignKey(UserCheckout)
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)

    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.street, self.city, self.country, self.zipcode)

    def get_address(self):
        return "{0}, {1}, {2}, {3}".format(self.street, self.city, self.country, self.zipcode)

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('completed', 'Completed')
)

class Order(models.Model):
    cart = models.ForeignKey(Cart)
    user = models.ForeignKey(UserCheckout, null=True)
    shipping_address= models.ForeignKey(UserAddress, related_name='billing_address', null=True)
    billing_address=models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
    shipping_total_price = models.DecimalField(decimal_places=2, max_digits=50, default=5.99)
    order_total = models.DecimalField(decimal_places=2, max_digits=50)
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')

    def __str__(self):
        return str(self.cart.id)

    def mark_completed(self):
        self.status = "completed"
        self.save()

def order_pre_save(sender, instance,*args, **kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total
    # instance.save() <- you don't save when you pre-save... remember!

pre_save.connect(order_pre_save, sender=Order)
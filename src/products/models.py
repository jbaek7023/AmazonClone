from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.safestring import mark_safe

class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(categories = instance.categories.all())
        products_two = self.get_queryset().filter(default = instance.default)

        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        # return self.get_queryset()
        return qs

def image_upload_to_featured(instance, filename):
    title = instance.product.title
    slug = slugify(title)

    return "products/{0}/featured/{1}".format(slug, filename)




# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=3, max_digits=30)
    active = models.BooleanField(default=True)
    objects = ProductManager()

    categories = models.ManyToManyField('Category', blank=True)
    default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)

    #inventory
    #slug

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk":self.pk})

    def get_image_url(self):
        img = self.productimage_set.first()
        if img:
            return img.image.url
        return img #None

    def get_category(self):
        return self.default

class ProductFeatured(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=image_upload_to_featured)
    title = models.CharField(max_length=120, null=True, blank=True)
    text= models.CharField(max_length=120, null=True, blank=True)
    text_right = models.BooleanField(default=False)
    show_price = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    make_image_background = models.BooleanField(default=False)
    text_css_color = models.CharField(max_length=120, null=True, blank=True)


    def __str__(self):
        return self.product.title

class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug= models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"pk": self.pk})


class Variation(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(null=True, blank=True) #refer none == to unlimited amount

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_html_price(self):
        if self.sale_price is not None:
            html_text = "<span class='sale-price'>{0}</span> <span class='og-price'>{1}</span>".format(self.sale_price, self.price)
            return mark_safe(html_text)
        else:
            html_text = "<span class='sale-price'>{0}</span>".format(self.price)
            return mark_safe(html_text)


    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def add_to_cart(self):
        return "{0}?item={1}&qty=1".format(reverse("carts"), self.id)

    def remove_from_cart(self):
        return "{0}?item={1}&qty=1&delete=True".format(reverse("carts"), self.id)

    def get_title(self):
        return "{0} - {1}".format(self.product.title, self.title)

def product_saved_receiver(sender, instance, created, *args, **kwargs):
    print(sender)
    print(instance)
    print(created)

    product = instance
    variations = product.variation_set.all()
    # variations = Variation.objects.filter(product=product)
    if variations.count() ==0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        new_var.save()

post_save.connect(product_saved_receiver, sender=Product)

def image_upload_to(instance, filename):
    title = instance.product.title
    slug = slugify(title)

    return "products/{0}/{1}".format(slug, filename)

# Product Images
class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=image_upload_to)

    def __str__(self):
        return self.product.title
from django.contrib import admin
from .models import Product, Variation, ProductImage, Category, ProductFeatured

class VariationInline(admin.TabularInline):
    model = Variation
    extra = 0

class ProductInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','price','description', 'active']
    inlines = [
        VariationInline,
        ProductInline,
    ]
    class Meta:
        model = Product

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(ProductFeatured)


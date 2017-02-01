from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
# Create your views here.
from django.utils import timezone

from .models import Product

class ProductDetailView (DetailView):
    model = Product
    #template_name = "appname/modelname_detail.html"

class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data()
        context["now"] = timezone.now()

        print(context)

        return context


#
# def product_detail_view_func(request, id):
#
#     product_instance = Product.object.get(id=id)
#     template = "products/product_detail.html"
#     context = {
#         "object" : product_instance
#     }
#     return render(request, template, context)
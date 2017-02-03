from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
# Create your views here.
from django.utils import timezone
from django.db.models import Q

from .models import Product, Variation, Category
from .forms import VariationInventoryFormSet
from .mixins import StaffRequiredMixin, LoginRequiredMixin

from django.contrib import messages

class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()

class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_product = obj.default_category.all()
        products = (product_set | default_product).distinct()
        context["products"] = products
        return context

class VariationListView(LoginRequiredMixin,ListView):
    model = Variation
    queryset = Variation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(VariationListView, self).get_context_data()
        context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
        return context

    # Override query set
    def get_queryset(self, *args, **kwargs):
        # qs = super(VariationListView, self).get_queryset(*args, **kwargs)
        # query = self.request.GET.get("q")
        # print(kwargs)
        product_pk = self.kwargs.get("pk")
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            queryset = Variation.objects.filter(product= product)
        return queryset

    def post(self, request, *args, **kwargs):
        formset = VariationInventoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                new_item = form.save(commit=False)
                if new_item.title:
                    product_pk = self.kwargs.get("pk")
                    product = get_object_or_404(Product, pk=product_pk)
                    new_item.product = product
                    new_item.save()
            messages.success(request, "Your Inventory has been updated.")
            return redirect("product_list")
        raise Http404

import random
class ProductDetailView (DetailView):
    model = Product
    #template_name = "appname/modelname_detail.html"

    def get_context_data(self, *args,**kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        # random order. top 6 objects
        # context["related"] = Product.objects.get_related(self.get_object()).order_by("?")[:6]

        rel_args = Product.objects.get_related(self.get_object()).order_by("?")[:6]
        rel_kwargs_key = lambda x:random.random()
        context["related"] = sorted(rel_args, key= rel_kwargs_key)


        return context

class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data()
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q", True) #True is default

        return context

    # Override query set
    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            # qs = self.model.objects.filter(title__icontiains=query)
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            try:
                qs2 = self.model.objects.filter(
                    Q(price__icontains=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs

#
# def product_detail_view_func(request, id):
#
#     product_instance = Product.object.get(id=id)
#     template = "products/product_detail.html"
#     context = {
#         "object" : product_instance
#     }
#     return render(request, template, context)
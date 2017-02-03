from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin


from .views import ProductDetailView, ProductListView, VariationListView,CategoryListView, CategoryDetailView

urlpatterns = [
    # Examples:
    # url(r'^(?P<id>\d+)', 'products.views.product_detail_view_func', name='product_detail_function'),
    url(r'^$', CategoryListView.as_view(), name='category_list'),
    url(r'^(?P<pk>\d+)/$', CategoryDetailView.as_view(), name='category_detail'),

]

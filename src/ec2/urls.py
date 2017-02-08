from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from carts.views import CartView, ItemCountView, CheckOutView, CheckoutFinalView
from orders.views import AddressSelectFormView, UserAddressCreateView, OrderList, OrderDetail

urlpatterns = [
    # Examples:
    url(r'^$', 'newsletter.views.home', name='home'),
    url(r'^contact/$', 'newsletter.views.contact', name='contact'),
    url(r'^about/$', 'ec2.views.about', name='about'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^products/', include('products.urls')),
    url(r'^category/', include('products.urls_category')),
    url(r'^orders/$', OrderList.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name='order_detail'),
    url(r'^carts/$', CartView.as_view(), name='carts'),
    url(r'^carts/count/$', ItemCountView.as_view(), name='item_count'),
    url(r'^checkout/$', CheckOutView.as_view(), name='checkout'),
    url(r'^checkout/address/$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout/address/create/$', UserAddressCreateView.as_view(), name='user_create_address'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
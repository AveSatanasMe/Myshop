#E:\Q\myshop\myshop\urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('', RedirectView.as_view(url=f'/{settings.LANGUAGE_CODE}/', permanent=False)),
    path('i18n/', include('django.conf.urls.i18n')),
] + i18n_patterns(
    path('admin/', admin.site.urls),
    path(_('cart/'), include('cart.urls', namespace='cart')),
    path(_('orders/'), include('orders.urls', namespace='orders')),
    path(_('coupons/'), include('coupons.urls', namespace='coupons')),
    path('rosetta/', include('rosetta.urls')),
    path('', include('shop.urls', namespace='shop')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

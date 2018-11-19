from django.conf.urls import url
from . import views

urlpatterns = [
    # /cart/
    url(r'^$', views.CartView.as_view(), name='cart'),
]

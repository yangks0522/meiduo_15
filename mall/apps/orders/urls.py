from django.conf.urls import url
from . import views

urlpatterns = [
    #/orders/places/
    url(r'^places/$',views.PlaceOrderView.as_view(),name='placeorder'),
    url(r'^$',views.OrderCreateAPIView.as_view(),name='order'),
]
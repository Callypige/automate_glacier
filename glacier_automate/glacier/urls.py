from django.urls import path

from glacier.views import create_order, order_detail, retrieve_order

urlpatterns = [
    path('', create_order, name='create_order'),
    path('details_order/<str:order_id>/', order_detail, name='order_detail'),
    path('retrieve_order/', retrieve_order, name='retrieve_order'),
    # path('fill-pot/', fill_pot, name='fill_pot'),
]

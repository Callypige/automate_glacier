from django.contrib import admin

from .models import Flavor, Order, OrderFlavor

admin.site.register(Flavor)
admin.site.register(Order)
admin.site.register(OrderFlavor)

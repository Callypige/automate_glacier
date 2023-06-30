from django.shortcuts import redirect, get_object_or_404
from glacier.models import Flavor, Order, OrderFlavor
from django.template import loader
from django.http import HttpResponse


def create_order(request):
    flavors = Flavor.objects.all()

    if request.method == "POST":
        order = Order.objects.create()
        for flavor in flavors:
            quantity = int(request.POST.get(str(flavor.id), 0))
            if quantity > 0:
                OrderFlavor.objects.create(
                    order=order, flavor=flavor, quantity=quantity
                )

        order.generate_order_code()
        return redirect("order_detail", order_id=order.id)

    template = loader.get_template("glacier/create_order.html")
    context = {"flavors": flavors}
    return HttpResponse(template.render(context, request))


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    flavors = OrderFlavor.objects.filter(order=order)
    total_price = order.calculate_total_price()

    template = loader.get_template("glacier/order_detail.html")
    context = {"order": order, "flavors": flavors, "total_price": total_price}
    return HttpResponse(template.render(context, request))


def retrieve_order(request):
    if request.method == "POST":
        order_code = request.POST.get("order_code")
        order = get_object_or_404(Order, code=order_code)
        return redirect("order_detail", order_id=order.id)

    template = loader.get_template("glacier/retrieve_order.html")
    context = {}

    return HttpResponse(template.render(context, request))

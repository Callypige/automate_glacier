from django.db import models


class Flavor(models.Model):
    name = models.CharField(max_length=255)
    price_per_scoop = models.DecimalField(max_digits=5, decimal_places=2)
    quantity_available = models.IntegerField(default=40)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.name

    def fill_up_flavor(self):
        quantity_added = 40 - self.quantity_available
        self.quantity_available = 40
        self.save()
        return quantity_added


class Order(models.Model):
    flavors = models.ManyToManyField(Flavor, through="OrderFlavor")

    def calculate_total_price(self):
        total_price = 0
        for order_flavor in self.orderflavor_set.all():
            total_price += order_flavor.quantity * order_flavor.flavor.price_per_scoop
        return total_price

    def display_order(self):
        print("Order:")
        for order_flavor in self.orderflavor_set.all():
            print(f"{order_flavor.flavor.name} ({order_flavor.quantity} boules)")

    def __str__(self):
        return f"Order #{self.id}"


class OrderFlavor(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    flavor = models.ForeignKey(Flavor, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.quantity > self.flavor.quantity_available:
            raise ValueError("Quantité insuffisante de parfum disponible.")
        self.flavor.quantity_available -= self.quantity
        self.flavor.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.flavor.quantity_available += self.quantity
        self.flavor.save()
        super().delete(*args, **kwargs)

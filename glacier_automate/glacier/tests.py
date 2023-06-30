from django.test import TestCase
from glacier.models import Flavor, Order, OrderFlavor
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO


class CreateFlavorsCommandTestCase(TestCase):
    def test_create_flavors_command(self):
        out = StringIO()
        call_command("load_initial_data", stdout=out)
        output = out.getvalue()

        flavors = Flavor.objects.all()
        # Check that all 5 flavors have been created
        self.assertEqual(len(flavors), 5)

        for flavor in flavors:
            self.assertIn(
                flavor.name, output
            )  # Check that the flavor name is present in the output

            # Check that the flavor image has been correctly saved
            self.assertTrue(flavor.image)
            self.assertTrue(flavor.image.name.startswith("images/"))

        self.assertIn("Created flavor: Chocolat Orange", output)
        self.assertIn("Created flavor: Sirop d'érable Noix", output)
        self.assertIn("Created flavor: Menthe Chocolat", output)
        self.assertIn("Created flavor: Vanille Fraise Chocolat", output)
        self.assertIn("Created flavor: Chocolat Blanc Framboise", output)


class FlavorOrderIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create flavors
        cls.flavor1 = Flavor.objects.create(
            name="Chocolat Orange", price_per_scoop=2.0, quantity_available=40
        )
        cls.flavor2 = Flavor.objects.create(
            name="Sirop d'érable Noix", price_per_scoop=2.0, quantity_available=40
        )
        cls.flavor3 = Flavor.objects.create(
            name="Menthe Chocolat", price_per_scoop=2.0, quantity_available=40
        )
        cls.flavor4 = Flavor.objects.create(
            name="Vanille Fraise Chocolat", price_per_scoop=2.0, quantity_available=40
        )
        cls.flavor5 = Flavor.objects.create(
            name="Chocolat Blanc Framboise", price_per_scoop=2.0, quantity_available=40
        )

        # Create order
        cls.order = Order.objects.create()

    def test_fill_up_flavor(self):
        quantity_added = self.flavor1.fill_up_flavor()
        self.assertEqual(
            quantity_added, 0
        )  # Flavor already had maximum quantity available
        self.assertEqual(self.flavor1.quantity_available, 40)

        self.flavor1.quantity_available = 30
        quantity_added = self.flavor1.fill_up_flavor()
        self.assertEqual(quantity_added, 10)  # Flavor quantity increased by 10
        self.assertEqual(self.flavor1.quantity_available, 40)

    def test_orderflavor_create_updates_flavor_quantity(self):
        OrderFlavor.objects.create(order=self.order, flavor=self.flavor1, quantity=2)
        self.assertEqual(self.flavor1.quantity_available, 38)

    def test_orderflavor_create_with_insufficient_quantity_raises_error(self):
        with self.assertRaises(ValueError):
            OrderFlavor.objects.create(
                order=self.order, flavor=self.flavor1, quantity=50
            )

        # Verify that the Flavor quantity has been updated
        self.assertEqual(self.flavor1.quantity_available, 40)

    def test_order_calculate_total_price(self):
        order_flavor1 = OrderFlavor.objects.create(
            order=self.order, flavor=self.flavor1, quantity=2
        )
        order_flavor2 = OrderFlavor.objects.create(
            order=self.order, flavor=self.flavor2, quantity=3
        )
        order_flavor3 = OrderFlavor.objects.create(
            order=self.order, flavor=self.flavor3, quantity=1
        )

        total_price = self.order.calculate_total_price()
        expected_price = (
            (order_flavor1.quantity * order_flavor1.flavor.price_per_scoop)
            + (order_flavor2.quantity * order_flavor2.flavor.price_per_scoop)
            + (order_flavor3.quantity * order_flavor3.flavor.price_per_scoop)
        )
        self.assertEqual(total_price, expected_price)

    def test_order_generate_order_code(self):
        self.order.generate_order_code()
        self.assertIsNotNone(self.order.code)
        self.assertEqual(len(self.order.code), 10)

    def test_order_string_representation(self):
        self.assertEqual(str(self.order), f"Order #{self.order.id}")

    def test_order_one_scoop_of_each_flavor(self):
        flavors = [self.flavor1, self.flavor2, self.flavor3, self.flavor4, self.flavor5]

        # Order one scoop of each flavor
        for flavor in flavors:
            OrderFlavor.objects.create(order=self.order, flavor=flavor, quantity=1)

        # Calculate the expected total price
        expected_price = sum(flavor.price_per_scoop for flavor in flavors)

        # Generate the order code
        self.order.generate_order_code()

        # Verify the order code and total price
        self.assertIsNotNone(self.order.code)
        self.assertEqual(len(self.order.code), 10)
        self.assertEqual(self.order.calculate_total_price(), expected_price)

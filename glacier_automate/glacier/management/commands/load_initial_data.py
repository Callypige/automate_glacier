import os
from django.core.files import File
from django.core.management.base import BaseCommand
from glacier.models import Flavor


class Command(BaseCommand):
    def handle(self, *args, **options):
        flavors = [
            {
                "name": "Chocolat Orange",
                "price_per_scoop": 2.5,
                "quantity_available": 40,
                "image_path": "images/chocolat-orange.png",
            },
            {
                "name": "Sirop d'érable Noix",
                "price_per_scoop": 3.0,
                "quantity_available": 40,
                "image_path": "images/maple-walnut.png",
            },
            {
                "name": "Menthe Chocolat",
                "price_per_scoop": 2.8,
                "quantity_available": 40,
                "image_path": "images/mint-chocolat.png",
            },
            {
                "name": "Vanille Fraise Chocolat",
                "price_per_scoop": 2.7,
                "quantity_available": 40,
                "image_path": "images/strawberry-vanille-chocolate.png",
            },
            {
                "name": "Chocolat Blanc Framboise",
                "price_per_scoop": 3.2,
                "quantity_available": 40,
                "image_path": "images/white-chocolate-raspberry.png",
            },
        ]

        for flavor_data in flavors:
            try:
                flavor = Flavor.objects.get(name=flavor_data["name"])
                self.stdout.write(
                    self.style.ERROR(
                        f"Flavor '{flavor.name}' already exists. Skipping creation."
                    )
                )
                continue
            except Flavor.DoesNotExist:
                pass

            image_path = flavor_data["image_path"]
            image_full_path = os.path.join(os.getcwd(), image_path)

            try:
                with open(image_full_path, "rb") as f:
                    flavor = Flavor.objects.create(
                        name=flavor_data["name"],
                        price_per_scoop=flavor_data["price_per_scoop"],
                        quantity_available=flavor_data["quantity_available"],
                    )
                    flavor.image.save(os.path.basename(image_full_path), File(f))
                    self.stdout.write(
                        self.style.SUCCESS(f"Created flavor: {flavor.name}")
                    )
            except FileNotFoundError:
                raise FileNotFoundError(f"Image file '{image_full_path}' not found.")
            except Exception as e:
                raise Exception(f"An error occurred while creating flavor: {e}")

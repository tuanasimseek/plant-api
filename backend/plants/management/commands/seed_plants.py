from django.core.management.base import BaseCommand
from plants.models import Plant
from plants.seed_data import PLANT_DATA


class Command(BaseCommand):
    help = "Bitki verilerini toplu ekler veya günceller"

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        for item in PLANT_DATA:
            plant, created = Plant.objects.update_or_create(
                scientific_name=item["scientific_name"],
                defaults={
                    "name": item["name"],
                    "category": item["category"],
                    "description": item["description"],
                    "watering_interval_days": item["watering_interval_days"],
                    "light_requirement": item["light_requirement"],
                    "temperature_min": item["temperature_min"],
                    "temperature_max": item["temperature_max"],
                    "image": item["image"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Oluşturuldu: {plant.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Güncellendi: {plant.name}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nTamamlandı. Oluşturulan: {created_count}, Güncellenen: {updated_count}"
        ))
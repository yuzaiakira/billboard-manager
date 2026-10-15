from django.core.management.base import BaseCommand

from siteoption.constants import (
    BILLBOARD_COMMISSION,
    BILLBOARD_VISIBILITY,
    SITE_NAME,
)
from siteoption.models import OptionModel


class Command(BaseCommand):
    help = "Import site options data to database"

    def get_default_data(self):
        return [
            {
                "key": BILLBOARD_COMMISSION,
                "type": OptionModel.FLOAT,
                "value": "1.2",
            },
            {
                "key": BILLBOARD_VISIBILITY,
                "type": OptionModel.BOOLEAN,
                "value": "True",
            },
            {
                "key": SITE_NAME,
                "type": OptionModel.STRING,
                "value": "My Site",
            },
        ]

    def handle(self, *args, **kwargs):
        self.stdout.write("Ready to import data ...")
        for item in self.get_default_data():
            OptionModel.objects.get_or_create(
                key=item["key"],
                defaults={"type": item["type"], "value": item["value"]},
            )
        self.stdout.write(self.style.SUCCESS("All data imported."))

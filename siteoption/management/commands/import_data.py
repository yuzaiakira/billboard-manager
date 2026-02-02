from django.core.management.base import BaseCommand
from siteoption.models import OptionModel

class Command(BaseCommand):
    help = 'import site options data to database'

    def default_data(self, *args, **kwargs):
        OptionModel.objects.get_or_create(type=OptionModel.FLOAT,
                                          key="BillboardCommission",
                                          value=1.2)

        OptionModel.objects.get_or_create(type=OptionModel.BOOLEAN,
                                          key="BillboardVisibility",
                                          value=True)
        
        OptionModel.objects.get_or_create(type=OptionModel.STRING,
                                          key="SiteName",
                                          value=True)


    def handle(self, *args, **kwargs):
        self.stdout.write("ready to import data ...")

        self.default_data()

        self.stdout.write(
            self.style.SUCCESS("all data is importing")
                               )
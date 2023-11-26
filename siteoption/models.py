from django.db import models

# Create your models here.


class OptionModel(models.Model):
    INTEGER = 0
    STRING = 1
    FLOAT = 2
    BOOLEAN = 3

    type_group_status = (
        (INTEGER, "integer"),
        (STRING, "string"),
        (FLOAT, "float"),
        (BOOLEAN, "boolean"),
    )

    type = models.PositiveSmallIntegerField(choices=type_group_status, default=1)

    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()

    def clean_value(self):
        if self.type == self.INTEGER:
            return int(self.value)
        elif self.type == self.STRING:
            return str(self.value)
        elif self.type == self.FLOAT:
            return float(self.value)
        elif self.type == self.BOOLEAN:
            if self.value == "false" or self.value == "False" or self.value == "0":
                return False
            return bool(self.value)


    def __str__(self):
        return self.key


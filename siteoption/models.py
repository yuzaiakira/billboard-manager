from django.db import models

# Create your models here.


class OptionModel(models.Model):
    INTEGER = 0
    STRING = 1
    FLOAT = 2
    DOUBLE = 3
    BOOLEAN = 4

    type_group_status = (
        (INTEGER, "integer"),
        (STRING, "string"),
        (FLOAT, "float"),
        (DOUBLE, "double"),
        (BOOLEAN, "boolean"),
    )

    type = models.PositiveSmallIntegerField(choices=type_group_status, default=1)

    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()


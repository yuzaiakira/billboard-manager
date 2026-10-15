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

    class Meta:
        verbose_name = "Site option"
        verbose_name_plural = "Site options"

    def clean_value(self):
        if self.type == self.INTEGER:
            try:
                return int(self.value)
            except ValueError as e:
                raise ValueError(f"Invalid integer for key '{self.key}': {self.value!r}") from e
        elif self.type == self.STRING:
            return str(self.value)
        elif self.type == self.FLOAT:
            try:
                return float(self.value)
            except ValueError as e:
                raise ValueError(f"Invalid float for key '{self.key}': {self.value!r}") from e
        elif self.type == self.BOOLEAN:
            raw = (self.value or "").strip().lower()
            if raw in ("true", "1", "yes"):
                return True
            if raw in ("false", "0", "no"):
                return False
            raise ValueError(f"Invalid boolean for key '{self.key}': {self.value!r}")
        return self.value

    def __str__(self):
        return self.key


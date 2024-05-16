import os
from uuid import uuid4
from django.utils.timezone import now
from django.core.files.storage import default_storage


def billboard_path(instance, filename):
    # Create a date-based file path
    date_today = now().date()
    date_path = date_today.strftime('billboard/%Y/%m/%d')

    # Prepare the full file path
    full_path = os.path.join(date_path, filename)

    # If the file already exists, prepend a UUID to the filename
    if default_storage.exists(full_path):
        filename = "{0}-{1}".format(str(uuid4())[:8], filename)
        full_path = os.path.join(date_path, filename)

    return full_path

def billboard_bool_value(value):
    if value:
        return "دارد"
    return "ندارد"

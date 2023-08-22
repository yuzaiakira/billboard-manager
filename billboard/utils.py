from uuid import uuid4


def billboard_path(instance, filename):
    return 'billboard/{0}-{1}'.format(str(uuid4())[:8], filename)

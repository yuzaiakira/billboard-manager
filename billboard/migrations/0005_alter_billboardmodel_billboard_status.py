# Generated manually — choices label update only (non-destructive)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billboard', '0004_auto_20250515_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billboardmodel',
            name='billboard_status',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, 'نمایش در سایت'),
                    (1, 'پیش نویس'),
                    (2, 'آرشیو'),
                    (3, 'غیر قابل اکران'),
                ],
                default=0,
                verbose_name='وضعیت بیلبورد',
            ),
        ),
    ]

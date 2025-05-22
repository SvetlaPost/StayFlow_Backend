from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0003_alter_rent_daily_price_alter_rent_description_and_more'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='location',
            field=models.ForeignKey(
                to='location.Location',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rents',
                help_text='Select the location (city/area) where the property is situated.',
                null=True,  # временно null=True, чтобы миграция не упала
            ),
        ),
    ]

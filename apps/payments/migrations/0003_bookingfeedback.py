# Generated by Django 5.2.1 on 2025-05-29 18:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_booking_base_price_booking_commission_percent_and_more'),
        ('payments', '0002_payment_host_fee_payment_is_refunded'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('comment', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='booking.booking')),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]

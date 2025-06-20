# Generated by Django 5.1.7 on 2025-06-02 19:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Lot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ticker", models.CharField(max_length=10)),
                ("date_purchased", models.DateField()),
                ("shares", models.DecimalField(decimal_places=2, max_digits=10)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nlv_goal",
                    models.DecimalField(
                        decimal_places=2, default=250000.0, max_digits=12
                    ),
                ),
                (
                    "monthly_goal",
                    models.DecimalField(
                        decimal_places=2, default=12000.0, max_digits=10
                    ),
                ),
                (
                    "nav_goal",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "marginal_tax_rate",
                    models.DecimalField(decimal_places=2, default=0.37, max_digits=4),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

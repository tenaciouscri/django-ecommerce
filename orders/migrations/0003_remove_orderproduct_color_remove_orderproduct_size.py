# Generated by Django 4.0.1 on 2022-02-14 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_alter_order_state"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderproduct",
            name="color",
        ),
        migrations.RemoveField(
            model_name="orderproduct",
            name="size",
        ),
    ]

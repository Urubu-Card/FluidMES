from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("plantas", "0005_planta_suspensa_desde"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sensor",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("volume", "Volume"),
                    ("temperatura", "Temperatura"),
                    ("pressao", "Pressão"),
                    ("vazao", "Vazão"),
                    ("processo", "Variável de processo"),
                ],
                max_length=20,
            ),
        ),
    ]

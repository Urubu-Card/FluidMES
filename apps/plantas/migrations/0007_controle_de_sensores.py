from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("plantas", "0006_variavel_processo"),
    ]

    operations = [
        migrations.AddField(
            model_name="clp",
            name="escrita_habilitada",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sensor",
            name="gravavel",
            field=models.BooleanField(default=False),
        ),
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
                    ("nivel", "Nível"),
                    ("tempo", "Tempo"),
                ],
                max_length=20,
            ),
        ),
    ]

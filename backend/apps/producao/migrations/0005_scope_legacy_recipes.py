from django.db import migrations


def scope_recipes(apps, schema_editor):
    Recipe = apps.get_model("producao", "Receita")
    Order = apps.get_model("producao", "Pedido")
    for recipe in Recipe.objects.filter(empresa__isnull=True).iterator():
        companies = list(
            Order.objects.filter(receita=recipe)
            .values_list("empresa_id", flat=True)
            .distinct()
        )
        for index, company in enumerate(companies):
            if index == 0:
                Recipe.objects.filter(pk=recipe.pk).update(empresa_id=company)
            else:
                fields = {
                    field: getattr(recipe, field)
                    for field in (
                        "nome",
                        "ingrediente1",
                        "ingrediente2",
                        "ingrediente3",
                        "tempo1",
                        "tempo2",
                    )
                }
                copy = Recipe.objects.create(empresa_id=company, **fields)
                Order.objects.filter(receita_id=recipe.pk, empresa_id=company).update(
                    receita_id=copy.pk
                )
        # Unreferenced recipes stay quarantined (empresa=NULL), never exposed across tenants.


class Migration(migrations.Migration):
    dependencies = [
        ("producao", "0004_pedido_concluido_em_pedido_quantidade_boa_and_more")
    ]
    operations = [migrations.RunPython(scope_recipes, migrations.RunPython.noop)]

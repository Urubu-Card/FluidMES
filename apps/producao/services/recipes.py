"""Recipe snapshots and sequential dosing/mixing stages; all volumes are litres."""

from copy import deepcopy

DEMO_FLOW_L_MIN = 30.0  # Adjustable demonstration parameter, not an industry average.


def components(recipe):
    if recipe.componentes:
        return deepcopy(recipe.componentes)
    return [
        dict(nome=f"Ingrediente {i}", quantidade_l=value, vazao_l_min=DEMO_FLOW_L_MIN)
        for i, value in enumerate(
            (recipe.ingrediente1, recipe.ingrediente2, recipe.ingrediente3), 1
        )
        if value > 0
    ]


def snapshot(recipe):
    return dict(
        id=recipe.pk,
        nome=recipe.nome,
        versao=recipe.versao,
        componentes=components(recipe),
        mistura1_seg=recipe.tempo1,
        mistura2_seg=recipe.tempo2 if len(components(recipe)) == 3 else 0,
    )


def coefficients(recipe):
    parts = recipe["componentes"]
    if len(parts) not in (2, 3):
        raise ValueError(
            "Revise a receita: são necessários dois ou três ingredientes com quantidade positiva."
        )
    base = sum(p["quantidade_l"] for p in parts)
    if base <= 0:
        raise ValueError("Receita sem composição válida. Revise seus ingredientes.")
    per_litre = sum(60 * (p["quantidade_l"] / base) / p["vazao_l_min"] for p in parts)
    mixing = recipe["mistura1_seg"] + (recipe["mistura2_seg"] if len(parts) == 3 else 0)
    return per_litre, mixing


def stages(recipe, volume, setup=0):
    result = []
    if setup:
        result.append(
            dict(
                tipo="reset", nome="Preparação para troca de receita", duracao_seg=setup
            )
        )
    base = sum(p["quantidade_l"] for p in recipe["componentes"])
    for index, part in enumerate(recipe["componentes"]):
        amount = volume * part["quantidade_l"] / base
        result.append(
            dict(
                tipo="dosagem",
                nome=part["nome"],
                quantidade_l=amount,
                vazao_l_min=part["vazao_l_min"],
                duracao_seg=60 * amount / part["vazao_l_min"],
            )
        )
        if index >= 1:
            result.append(
                dict(
                    tipo="mistura",
                    nome=f"Mistura {index}",
                    duracao_seg=recipe[f"mistura{index}_seg"],
                )
            )
    return result

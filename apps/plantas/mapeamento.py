"""Cadastro das tags de mapeamento.xlsx como sensores de um CLP."""

from rest_framework.exceptions import ValidationError

from services.modbus_map import TAGS
from .models import Sensor


def aplicar(clp):
    """Cria as tags que faltam; preserva as existentes. Devolve (novas, existentes)."""
    por_nome = {tag.nome: tag for tag in TAGS}
    por_endereco = {(tag.tipo_registro, tag.endereco): tag for tag in TAGS}
    encontrados = set()
    for sensor in clp.sensores.all():
        tag_nome = por_nome.get(sensor.nome)
        tag_endereco = por_endereco.get((sensor.tipo_registro, sensor.endereco))
        if tag_nome is None and tag_endereco is None:
            continue
        if tag_nome != tag_endereco or tag_nome in encontrados:
            raise ValidationError({
                "detail": (
                    f"O sensor {sensor.nome} conflita com a planilha. "
                    "Revise o nome, o tipo e o endereço antes de aplicar o mapa."
                )
            })
        encontrados.add(tag_nome)
    novos = [
        Sensor(
            clp=clp,
            nome=tag.nome,
            tipo=tag.tipo,
            gravavel=tag.gravavel,
            tipo_registro=tag.tipo_registro,
            endereco=tag.endereco,
            unidade="bit" if tag.tipo_registro == "coil" else "bruto",
            minimo=0,
            maximo=1 if tag.tipo_registro == "coil" else 65535,
        )
        for tag in TAGS
        if tag not in encontrados
    ]
    Sensor.objects.bulk_create(novos)
    return len(novos), len(encontrados)

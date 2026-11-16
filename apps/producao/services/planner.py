"""Minimum makespan for independent tanks with fixed mixing and linear dosing.

A feasibility search considers tank capacity, existing reservations, changeover,
parallel batches and repeated cycles. It does not assume shared pumps or pipes.
"""

import math
from dataclasses import dataclass
from .recipes import coefficients, stages

EPS = 1e-6
MAX_BATCHES = 2000


@dataclass(frozen=True)
class Tank:
    id: int
    name: str
    capacity: float
    ready: float = 0
    setup: float = 0
    preferred: bool = False
    note: str = ""


def schedule(recipe, quantity, tanks):
    if not math.isfinite(quantity) or quantity <= EPS:
        raise ValueError("Informe um volume positivo e finito.")
    tanks = [t for t in tanks if t.capacity > 0]
    if not tanks:
        raise ValueError(
            "Nenhuma planta liberada para produzir. Confira paradas, capacidade e comunicação dos CLPs."
        )
    if quantity > sum(t.capacity for t in tanks) * MAX_BATCHES:
        raise ValueError(
            "Pedido muito grande para as capacidades disponíveis. Divida o pedido."
        )
    rate, mixing = coefficients(recipe)

    def duration(volume):
        return mixing + rate * volume

    def capacity_by(tank, horizon):
        time = horizon - tank.ready - tank.setup
        if time <= 0:
            return 0.0
        full = math.floor(time / duration(tank.capacity))
        remainder = time - full * duration(tank.capacity)
        return full * tank.capacity + min(
            tank.capacity, max(0.0, (remainder - mixing) / rate)
        )

    def alone(tank):
        full = math.floor(quantity / tank.capacity)
        remainder = quantity - full * tank.capacity
        return (
            tank.ready
            + tank.setup
            + full * duration(tank.capacity)
            + (duration(remainder) if remainder > EPS else 0)
        )

    low, high = 0.0, min(alone(t) for t in tanks)
    if not math.isfinite(high) or high > 366 * 86400:
        raise ValueError(
            "A previsão ultrapassa um ano. Confira vazões, volumes e tempos da receita."
        )
    for _ in range(75):
        middle = (low + high) / 2
        if sum(capacity_by(t, middle) for t in tanks) >= quantity:
            high = middle
        else:
            low = middle
    remaining, batches = quantity, []
    # Completion time is primary; prefer less changeover, then the user's tank.
    for tank in sorted(tanks, key=lambda t: (t.setup, not t.preferred, t.ready, t.id)):
        assigned = min(remaining, capacity_by(tank, high + 1e-7))
        cursor, first = tank.ready, True
        while assigned > EPS:
            volume = min(tank.capacity, assigned)
            setup = tank.setup if first else 0
            finish = cursor + setup + duration(volume)
            batches.append(
                dict(
                    planta=tank.id,
                    planta_nome=tank.name,
                    quantidade=volume,
                    inicio_seg=cursor,
                    fim_seg=finish,
                    setup_seg=setup,
                    duracao_producao_seg=duration(volume),
                    etapas=stages(recipe, volume, setup),
                    motivo=(
                        tank.note
                        or (
                            "Reset configurado em zero."
                            if not tank.setup
                            else "Inclui preparação para troca de receita."
                        )
                    )
                    + (
                        " Aguarda liberação de produção já programada."
                        if tank.ready > EPS
                        else " Planta disponível agora."
                    ),
                )
            )
            if len(batches) > MAX_BATCHES:
                raise ValueError(
                    "O plano ultrapassa 2.000 ciclos. Divida o pedido ou ajuste as capacidades."
                )
            assigned -= volume
            remaining -= volume
            cursor, first = finish, False
        if remaining <= EPS:
            break
    if remaining > EPS:
        raise ValueError(
            "Não foi possível distribuir todo o volume. Revise as capacidades."
        )
    batches.sort(key=lambda b: (b["inicio_seg"], b["planta"]))
    return dict(
        lotes=batches,
        duracao_total_seg=max(b["fim_seg"] for b in batches),
        quantidade_total=quantity,
        plantas_qtd=len({b["planta"] for b in batches}),
        lotes_qtd=len(batches),
        setup_total_seg=sum(b["setup_seg"] for b in batches),
        criterio="Menor previsão de término; menor preparação e planta preferida como desempate.",
        estimativa=True,
    )

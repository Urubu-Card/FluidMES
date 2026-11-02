"""Simulador de CLPs Modbus TCP para a bancada do FluidMES."""

import argparse
import asyncio
from pathlib import Path
import sys

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "services"

from .modbus_simulation import build_mapped_context


def build_context():
    """Mapa genérico legado; endereços de protocolo 0–99, device_id=1."""
    return SimDevice(id=1, simdata=(
        [SimData(address=0, values=[False]*100, datatype=DataType.BITS)],
        [SimData(address=0, values=[False]*100, datatype=DataType.BITS, readonly=True)],
        [SimData(address=0, values=list(range(1000, 1100)), datatype=DataType.UINT16)],
        [SimData(address=0, values=list(range(100)), datatype=DataType.UINT16, readonly=True)],
    ))


async def servir(host, portas, *, legado, demo, modo=None):
    servidores = []
    try:
        for indice, porta in enumerate(portas):
            contexto = (
                build_context() if legado
                else build_mapped_context(demo=demo, atraso=5 * indice, modo=modo)
            )
            servidor = ModbusTcpServer(context=contexto, address=(host, porta))
            servidores.append(servidor)
            await servidor.serve_forever(background=True)
            print(f"CLP simulado {indice + 1}: {host}:{porta} (Unit ID 1)", flush=True)
        await asyncio.Future()
    finally:
        for servidor in reversed(servidores):
            await servidor.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5020)
    parser.add_argument("--segunda-porta", type=int, help="Porta de um segundo CLP independente.")
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--demo", action="store_true", help="Executa ciclos locais (modo 0) automaticamente.")
    modos.add_argument("--legado", action="store_true", help="Usa o mapa genérico anterior.")
    parser.add_argument(
        "--modo", type=int, choices=(0, 1, 2),
        help="MODO inicial dos tanques: 0 local, 1 aparelho, 2 MES (padrão: 2; 0 com --demo).",
    )
    args = parser.parse_args()
    portas = [args.port]
    if args.segunda_porta is not None:
        portas.append(args.segunda_porta)
    if len(set(portas)) != len(portas) or any(not 1 <= porta <= 65535 for porta in portas):
        parser.error("Use portas distintas entre 1 e 65535.")
    try:
        asyncio.run(servir(args.host, portas, legado=args.legado, demo=args.demo, modo=args.modo))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

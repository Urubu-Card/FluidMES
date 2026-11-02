"""Troca o MODO de um tanque do CLP SIMULADO (representa a chave da planta).

Uso: python services/definir_modo.py TK1 2 [--host 127.0.0.1] [--port 5020]
Modos: 0 operação local · 1 aparelho · 2 sistema MES.
Não use contra o CLP real: nele o modo é escolhido na própria planta.
"""

import argparse
import asyncio
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "services"

from .clp_control import Modbus_Control
from .modbus_map import ENDERECOS_TANQUES, MODOS


async def definir(host, port, tanque, modo):
    cliente = Modbus_Control(host, port)
    try:
        await cliente.Conectar()
        await cliente.Write_Register(ENDERECOS_TANQUES[tanque]["MODO"], modo)
    finally:
        cliente.conexao.FecharConexao()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tanque", choices=sorted(ENDERECOS_TANQUES))
    parser.add_argument("modo", type=int, choices=sorted(MODOS))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5020)
    args = parser.parse_args()
    asyncio.run(definir(args.host, args.port, args.tanque, args.modo))
    print(f"{args.tanque}: MODO {args.modo} · {MODOS[args.modo]}")


if __name__ == "__main__":
    main()

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Clp
from services.clp_control import Modbus_Control


@login_required
def plantas(request):
    """Dashboard de plantas — lista CLPs com status online/offline."""
    clps_registrados = Clp.objects.filter(planta__empresa=request.user.empresa)

    clps_context = []
    for clp in clps_registrados:
        online = False
        try:
            conexao = Modbus_Control(clp.ip, clp.porta)
            online = conexao.isConnected()
        except Exception:
            online = False

        clps_context.append({
            'id':     clp.idclp,
            'nome':   clp.nome,
            'ip':     clp.ip,
            'porta':  clp.porta,
            'online': online,
        })

    return render(request, 'pages/plantas.html', {'clps': clps_context})


@login_required
def teste_clp(request):
    """Página de teste manual de coils."""
    from services.clp_control import Modbus_Control

    IP   = '127.0.0.1'
    PORT = '5020'
    clp  = Modbus_Control(ip=IP, port=PORT)
    resposta = ''

    if request.method == 'POST':
        if request.POST.get('busca'):
            endereco = request.POST.get('adress')
            resposta = clp.Ler_Coil(int(endereco))
        elif request.POST.get('editar'):
            endereco = request.POST.get('endereco')
            valor    = bool(request.POST.get('valor'))
            resposta = clp.Escrever_Coil(int(endereco), valor)

    return render(request, 'pages/index.html', {
        'resposta': resposta,
        'cliente':  clp.cliente,
    })


@login_required
def status_clp(request):
    """Endpoint JSON para status dos CLPs (usado pelo frontend via fetch)."""
    HEADER_ESPERADO = 'WE1MSHR0cFJlcXVlc3Q='
    if request.headers.get('X-Requested-With') != HEADER_ESPERADO:
        return JsonResponse({'erro': 'não autorizado'}, status=401)

    clps_registrados = Clp.objects.filter(planta__empresa=request.user.empresa)
    conexoes = {}

    for clp in clps_registrados:
        try:
            conexoes[clp.idclp] = Modbus_Control(clp.ip, clp.porta)
        except Exception:
            conexoes[clp.idclp] = None

    status = {
        clp_id: bool(conn and conn.isConnected())
        for clp_id, conn in conexoes.items()
    }

    return JsonResponse({'clps': status})

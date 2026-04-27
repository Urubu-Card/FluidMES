from django.shortcuts import render ,redirect
from plasmic.clp_control import Modbus_Control
from django.http import JsonResponse

IP = "127.0.0.1"

PORT = "5020"

clp = Modbus_Control(ip=IP,port=PORT)

def teste_clp(request):
    
    resposta =""
    
    if request.method == "POST":
        busca = request.POST.get("busca")
        editar = request.POST.get("editar")
        
        
        if busca:
            endreco = request.POST.get("adress")
            resposta = clp.Ler_Coil(int(endreco))
          
        elif editar:
            endreco = request.POST.get("endereco")
            valor   = bool(request.POST.get("valor"))
            resposta = clp.Escrever_Coil(int(endreco),valor)
        
   

    
    return render(request,"index.html",{"resposta":resposta})

def status_coil(request):
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"erro": "não autorizado"}, status=403)
    
    estado = clp.Ler_Coil(4)
    
    return JsonResponse({"estado": estado})

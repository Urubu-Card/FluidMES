from django.shortcuts import render ,redirect ,get_object_or_404
from plasmic.clp_control import Modbus_Control
from django.http import JsonResponse
from .forms import Cadastro as Cadastrar 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate , login , logout


IP = "127.0.0.1"

PORT = "5020"


class Clp:

    def teste_clp(request):
        clp = Modbus_Control(ip=IP,port=PORT)
        
        resposta =""
        

        cliente = clp.cliente

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
        


        
        return render(request,"CLP/index.html",{"resposta":resposta,"cliente":cliente})

    def status(request):
        clp = Modbus_Control(ip=IP,port=PORT)
        
        if request.headers.get("X-Requested-With") != "WE1MSHR0cFJlcXVlc3Q=":
            return JsonResponse({"erro": "nao autorizado"}, status=401)
        
        
        else:
            estado = clp.Ler_Coil(4)
            
            return JsonResponse({"estado": estado,"cliente":bool(clp.cliente)})


class Autenticacao:


    def Cadastrar(request):

        if request.method == "POST":
            form = Cadastrar(request.POST)
            #print("a")
            if form.is_valid():
                print("Chega")
                form.save()
                return redirect("login")
        else:
            form = Cadastrar()


        return render(request,"Auth/cadastro.html",{"form":form}) 

    def Login(request):

        return render(request,"Auth/login.html")
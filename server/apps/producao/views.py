from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def pedidos(request):
    return render(request,'pages/pedidos.html',)

def rendimento(request):
    return render(request,'pages/rendimentos.html',)

def receitas(request):
    return render(request,'pages/receitas.html')
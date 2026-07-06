from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import Cadastro, Login as LoginForm


def landing_page(request):
    return render(request, 'index.html')


def cadastrar(request):
    if request.method == 'POST':
        form = Cadastro(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = Cadastro()
    return render(request, 'Auth/cadastro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('plantas')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.Autenticar(request)
            if usuario:
                login(request, usuario)
                return redirect('plantas')
            else:
                messages.error(request, 'CPF/E-mail ou senha incorretos.')
                return redirect('login')
        else:
            for campo, erros in form.errors.items():
                for erro in erros:
                    messages.error(request, erro)
            return redirect('login')

    return render(request, 'Auth/login.html', {'form': LoginForm()})


def logout_view(request):
    logout(request)
    return redirect('login')

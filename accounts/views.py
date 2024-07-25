from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.urls import reverse

# Realizar Registro de Usuário
def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Você está logado agora.')
            return redirect(reverse('spare_list'))  # Usando reverse para resolver a URL
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registro.html', {'form': form})

# Realizar Login
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bem-vindo, {username}!")
                return redirect(reverse('spare_list'))  # Usando reverse para resolver a URL
            else:
                messages.error(request, "Credenciais inválidas. Tente novamente.")
        else:
            messages.error(request, "Erro ao validar o formulário. Verifique os dados e tente novamente.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Realizar Logout
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Você saiu com sucesso.")
        return redirect(reverse('login'))  # Usando reverse para resolver a URL
    return render(request, 'logout.html')  # Renderize o template logout antes do logout

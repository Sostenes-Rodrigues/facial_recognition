from django.shortcuts import render

# Create your views here.
def dashboard(request):
	return render(request, "dashboard.html")


def usuarios(request):
	return render(request, "usuarios.html")


def turmas(request):
	return render(request, "turmas.html")


def registro(request):
	return render(request, "registro.html")


def permissoes(request):
	return render(request, "permissoes.html")

	
def suspensoes(request):
	return render(request, "suspensoes.html")


def acessoExterno(request):
	return render(request, "acessoExterno.html")	

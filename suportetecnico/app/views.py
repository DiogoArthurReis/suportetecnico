from django.shortcuts import render, redirect
from .models import Chamado, Usuario, Setor, Categoria
from django.utils import timezone


def dashboard(request):
    chamados = Chamado.objects.all()

    total_chamados = chamados.count()
    abertos = chamados.filter(status="ABERTO").count()
    em_atendimento = chamados.filter(status="EM_ATENDIMENTO").count()
    encerrados = chamados.filter(status="ENCERRADO").count()
    reabertos = chamados.filter(status="REABERTO").count()

    contexto = {
        "total_chamados": total_chamados,
        "abertos": abertos,
        "em_atendimento": em_atendimento,
        "encerrados": encerrados,
        "reabertos": reabertos,
    }

    return render(request, "chamados/dashboard.html", contexto)

def lista_chamados(request):
    chamados = Chamado.objects.all().order_by("-data_abertura")

    contexto = {
        "chamados": chamados
    }

    return render(request, "chamados/chamados.html", contexto)

def detalhe_chamado(request, id):
    chamado = Chamado.objects.get(id=id)

    contexto = {
        "chamado": chamado
    }

    return render(request, "chamados/chamado_detalhe.html", contexto)

def atribuir_tecnico(request, id):
    chamado = Chamado.objects.get(id=id)

    tecnicos = Usuario.objects.filter(tecnico=True)

    if request.method == "POST":
        tecnico_id = request.POST.get("tecnico")

        if tecnico_id:
            tecnico = Usuario.objects.get(id=tecnico_id)
            chamado.tecnico = tecnico
            chamado.save()

        return redirect("detalhe_chamado", id=id)

    contexto = {
        "chamado": chamado,
        "tecnicos": tecnicos,
    }

    return render(request, "chamados/atribuir_tecnico.html", contexto)

def alterar_status(request, id):
    chamado = Chamado.objects.get(id=id)

    if request.method == "POST":
        novo_status = request.POST.get("status")

        if novo_status == "EM_ATENDIMENTO":
            chamado.status = "EM_ATENDIMENTO"

            if chamado.data_inicio is None:
                chamado.data_inicio = timezone.now()

        elif novo_status == "ENCERRADO":
            chamado.status = "ENCERRADO"

            if chamado.data_encerramento is None:
                chamado.data_encerramento = timezone.now()

        elif novo_status == "REABERTO":
            chamado.status = "REABERTO"

        elif novo_status == "ABERTO":
            chamado.status = "ABERTO"

        chamado.save()

        return redirect("detalhe_chamado", id=id)

    contexto = {
        "chamado": chamado,
    }

    return render(request, "chamados/alterar_status.html", contexto)

def adicionar_resposta(request, id):
    chamado = Chamado.objects.get(id=id)

    usuarios = Usuario.objects.all()

    if request.method == "POST":
        usuario_id = request.POST.get("usuario")
        mensagem = request.POST.get("mensagem")

        if usuario_id and mensagem:
            usuario = Usuario.objects.get(id=usuario_id)

            chamado.respostas.create(
                usuario=usuario,
                mensagem=mensagem
            )

        return redirect("detalhe_chamado", id=id)

    contexto = {
        "chamado": chamado,
        "usuarios": usuarios,
    }

    return render(
        request,
        "chamados/adicionar_resposta.html",
        contexto
    )

def abrir_chamado(request):
    usuarios = Usuario.objects.all()
    setores = Setor.objects.all()
    categorias = Categoria.objects.all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descricao = request.POST.get("descricao")
        solicitante_id = request.POST.get("solicitante")
        setor_id = request.POST.get("setor")
        categoria_id = request.POST.get("categoria")
        prioridade = request.POST.get("prioridade")

        if titulo and descricao and solicitante_id and setor_id and categoria_id and prioridade:

            chamado = Chamado.objects.create(
                titulo=titulo,
                descricao=descricao,
                solicitante_id=solicitante_id,
                setor_id=setor_id,
                categoria_id=categoria_id,
                prioridade=prioridade,
                status="ABERTO"
            )

            return redirect("detalhe_chamado", id=chamado.id)

    contexto = {
        "usuarios": usuarios,
        "setores": setores,
        "categorias": categorias,
        "prioridades": Chamado.PRIORIDADE_CHOICES,
    }

    return render(
        request,
        "chamados/abrir_chamado.html",
        contexto
    )

from django.shortcuts import render, redirect, get_object_or_404
from .models import Chamado, Usuario, Setor, Categoria
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# =====================================================
# DECORADOR DE PERMISSÕES
# =====================================================

def perfil_requerido(*perfis_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def verificar_perfil(request, *args, **kwargs):

            usuario = Usuario.objects.filter(
                usuario_login=request.user
            ).first()

            if (
                usuario is None
                or not usuario.ativo
                or usuario.perfil not in perfis_permitidos
            ):
                return HttpResponseForbidden(
                    "Você não tem permissão para realizar esta ação."
                )

            return view_func(request, *args, **kwargs)

        return verificar_perfil

    return decorador


# =====================================================
# DASHBOARD
# =====================================================

@login_required
def dashboard(request):

    usuario = Usuario.objects.filter(
        usuario_login=request.user
    ).first()

    if usuario is None or not usuario.ativo:
        return HttpResponseForbidden(
            "Sua conta não está ativa ou vinculada ao sistema."
        )

    chamados = Chamado.objects.all()

    if usuario.perfil == "SOLICITANTE":
        chamados = chamados.filter(solicitante=usuario)

    contexto = {
        "usuario": usuario,
        "total_chamados": chamados.count(),
        "abertos": chamados.filter(status="ABERTO").count(),
        "em_atendimento": chamados.filter(
            status="EM_ATENDIMENTO"
        ).count(),
        "encerrados": chamados.filter(status="ENCERRADO").count(),
        "reabertos": chamados.filter(status="REABERTO").count(),
    }

    return render(
        request,
        "chamados/dashboard.html",
        contexto
    )


# =====================================================
# LISTA DE CHAMADOS
# =====================================================

@login_required
def lista_chamados(request):

    usuario = Usuario.objects.filter(
        usuario_login=request.user
    ).first()

    if usuario is None or not usuario.ativo:
        return HttpResponseForbidden(
            "Sua conta não está ativa ou vinculada ao sistema."
        )

    chamados = Chamado.objects.all().order_by("-data_abertura")

    if usuario.perfil == "SOLICITANTE":
        chamados = chamados.filter(solicitante=usuario)

    contexto = {
        "chamados": chamados,
        "usuario": usuario
    }

    return render(
        request,
        "chamados/chamados.html",
        contexto
    )


# =====================================================
# DETALHES DO CHAMADO
# =====================================================

@login_required
def detalhe_chamado(request, id):

    chamado = get_object_or_404(Chamado, id=id)

    usuario = Usuario.objects.filter(
        usuario_login=request.user
    ).first()

    if usuario is None or not usuario.ativo:
        return HttpResponseForbidden(
            "Sua conta não está ativa ou vinculada ao sistema."
        )

    if (
        usuario.perfil == "SOLICITANTE"
        and chamado.solicitante != usuario
    ):
        return HttpResponseForbidden(
            "Você não tem permissão para visualizar este chamado."
        )

    contexto = {
        "chamado": chamado,
        "usuario": usuario
    }

    return render(
        request,
        "chamados/chamado_detalhe.html",
        contexto
    )


# =====================================================
# ATRIBUIR TÉCNICO
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR")
def atribuir_tecnico(request, id):

    chamado = get_object_or_404(Chamado, id=id)

    tecnicos = Usuario.objects.filter(
        perfil="TECNICO",
        tecnico=True,
        ativo=True
    ).order_by("nome")

    if request.method == "POST":

        tecnico_id = request.POST.get("tecnico")

        if tecnico_id:

            tecnico = get_object_or_404(
                tecnicos,
                id=tecnico_id
            )

            chamado.tecnico = tecnico
            chamado.save()

        return redirect("detalhe_chamado", id=id)

    contexto = {
        "chamado": chamado,
        "tecnicos": tecnicos,
    }

    return render(
        request,
        "chamados/atribuir_tecnico.html",
        contexto
    )

# =====================================================
# ALTERAR STATUS
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR", "TECNICO")
def alterar_status(request, id):

    chamado = get_object_or_404(Chamado, id=id)

    usuario = Usuario.objects.filter(
        usuario_login=request.user,
        ativo=True
    ).first()

    if usuario is None:
        return HttpResponseForbidden(
            "Sua conta não está ativa."
        )

    status_validos = [
        "ABERTO",
        "EM_ATENDIMENTO",
        "ENCERRADO",
        "REABERTO"
    ]

    if request.method == "POST":

        novo_status = request.POST.get("status")

        if novo_status not in status_validos:
            return redirect("detalhe_chamado", id=id)

        # Técnicos não podem reabrir chamados
        if (
            usuario.perfil == "TECNICO"
            and novo_status == "REABERTO"
        ):
            return HttpResponseForbidden(
                "Técnicos não podem reabrir chamados."
            )

        chamado.status = novo_status

        if novo_status == "EM_ATENDIMENTO":

            if chamado.data_inicio is None:
                chamado.data_inicio = timezone.now()

            chamado.data_encerramento = None

        elif novo_status == "ENCERRADO":

            chamado.data_encerramento = timezone.now()

        else:
            chamado.data_encerramento = None

        chamado.save()

        return redirect("detalhe_chamado", id=id)

    contexto = {
        "chamado": chamado,
        "usuario": usuario,
    }

    return render(
        request,
        "chamados/alterar_status.html",
        contexto
    )

# =====================================================
# ADICIONAR RESPOSTA
# =====================================================

@login_required
def adicionar_resposta(request, id):

    chamado = get_object_or_404(Chamado, id=id)

    usuario = Usuario.objects.filter(
        usuario_login=request.user
    ).first()

    if usuario is None or not usuario.ativo:
        return HttpResponseForbidden(
            "Sua conta não está ativa ou vinculada ao sistema."
        )

    if (
        usuario.perfil == "SOLICITANTE"
        and chamado.solicitante != usuario
    ):
        return HttpResponseForbidden(
            "Você não tem permissão para responder a este chamado."
        )

    erro = None

    if request.method == "POST":

        mensagem = request.POST.get("mensagem", "").strip()

        if mensagem:

            chamado.respostas.create(
                usuario=usuario,
                mensagem=mensagem
            )

            return redirect("detalhe_chamado", id=id)

        erro = "Digite uma mensagem antes de enviar."

    return render(
        request,
        "chamados/adicionar_resposta.html",
        {
            "chamado": chamado,
            "erro": erro
        }
    )

# =====================================================
# SOLICITAR REABERTURA
# =====================================================

@login_required
def solicitar_reabertura(request, id):

    chamado = get_object_or_404(Chamado, id=id)

    usuario = Usuario.objects.filter(
        usuario_login=request.user,
        ativo=True
    ).first()

    if usuario is None or usuario.perfil != "SOLICITANTE":
        return HttpResponseForbidden(
            "Somente o solicitante pode solicitar a reabertura."
        )

    if chamado.solicitante != usuario:
        return HttpResponseForbidden(
            "Você não tem permissão para reabrir este chamado."
        )

    if chamado.status != "ENCERRADO":
        return HttpResponseForbidden(
            "Somente chamados encerrados podem ser reabertos."
        )

    erro = None

    if request.method == "POST":

        motivo = request.POST.get("motivo", "").strip()

        if not motivo:
            erro = "Informe o motivo da reabertura."

        else:

            with transaction.atomic():

                chamado.status = "REABERTO"
                chamado.data_encerramento = None
                chamado.save()

                chamado.respostas.create(
                    usuario=usuario,
                    mensagem="SOLICITAÇÃO DE REABERTURA: " + motivo
                )

            return redirect(
                "detalhe_chamado",
                id=chamado.id
            )

    return render(
        request,
        "chamados/solicitar_reabertura.html",
        {
            "chamado": chamado,
            "erro": erro,
        }
    )

# =====================================================
# ABRIR CHAMADO
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR", "SOLICITANTE")
def abrir_chamado(request):

    usuario_logado = Usuario.objects.get(
        usuario_login=request.user
    )

    if usuario_logado.perfil == "SOLICITANTE":
        usuarios = Usuario.objects.filter(
            id=usuario_logado.id
        )
    else:
        usuarios = Usuario.objects.filter(perfil="SOLICITANTE", ativo=True).order_by("nome")
    categorias = Categoria.objects.all().order_by("nome")

    erro = None

    if request.method == "POST":

        titulo = request.POST.get("titulo", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        solicitante_id = request.POST.get("solicitante")
        categoria_id = request.POST.get("categoria")
        prioridade = request.POST.get("prioridade")

        prioridades_validas = [
            valor for valor, nome in Chamado.PRIORIDADE_CHOICES
        ]

        solicitante = None

        if not titulo or not descricao or not categoria_id or not prioridade:
            erro = "Preencha todos os campos."

        elif usuario_logado.perfil == "SOLICITANTE":
            solicitante = usuario_logado

        elif not solicitante_id:
            erro = "Selecione um solicitante."

        else:
            solicitante = Usuario.objects.filter(
                id=solicitante_id
            ).first()

            if solicitante is None:
                erro = "Solicitante inválido."

        if erro is None:

            if solicitante.setor is None:
                erro = "O solicitante selecionado não possui um setor cadastrado."

        if erro is None:

            categoria = Categoria.objects.filter(
                id=categoria_id
            ).first()

            if categoria is None:
                erro = "Selecione uma categoria válida."

            elif prioridade not in prioridades_validas:
                erro = "Selecione uma prioridade válida."

        if erro is None:

            chamado = Chamado.objects.create(
                titulo=titulo,
                descricao=descricao,
                solicitante=solicitante,
                setor=solicitante.setor,
                categoria=categoria,
                prioridade=prioridade,
                status="ABERTO"
            )

            return redirect(
                "detalhe_chamado",
                id=chamado.id
            )

    contexto = {
        "usuarios": usuarios,
        "categorias": categorias,
        "prioridades": Chamado.PRIORIDADE_CHOICES,
        "erro": erro,
        "usuario": usuario_logado,
    }

    return render(
        request,
        "chamados/abrir_chamado.html",
        contexto
    )

# =====================================================
# LOGIN
# =====================================================

def login_usuario(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            perfil = Usuario.objects.filter(
                usuario_login=usuario
            ).first()

            if perfil is None or not perfil.ativo:
                return render(
                    request,
                    "chamados/login.html",
                    {
                        "erro": "Esta conta não está ativa no sistema."
                    }
                )

            login(request, usuario)

            return redirect("dashboard")

        return render(
            request,
            "chamados/login.html",
            {
                "erro": "Usuário ou senha inválidos."
            }
        )

    return render(
        request,
        "chamados/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_usuario(request):

    logout(request)

    return redirect("login")


# =====================================================
# LISTA DE USUÁRIOS
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR")
def lista_usuarios(request):

    usuarios = Usuario.objects.all().order_by("nome")

    contexto = {
        "usuarios": usuarios
    }

    return render(
        request,
        "chamados/usuarios.html",
        contexto
    )


# =====================================================
# CADASTRAR USUÁRIO
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR")
def cadastrar_usuario(request):

    setores = Setor.objects.all().order_by("nome")

    if request.method == "POST":

        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        setor_id = request.POST.get("setor")
        perfil = request.POST.get("perfil")
        username = request.POST.get("username", "").strip()
        senha = request.POST.get("senha", "")

        perfis_validos = [
            "ADMINISTRADOR",
            "TECNICO",
            "SOLICITANTE",
        ]

        erro = None
        erros_senha = []

        setor = Setor.objects.filter(id=setor_id).first()

        if not all([
            nome,
            email,
            setor_id,
            perfil,
            username,
            senha
        ]):
            erro = "Preencha todos os campos."

        elif perfil not in perfis_validos:
            erro = "Selecione um perfil válido."

        elif setor is None:
            erro = "Selecione um setor válido."

        elif User.objects.filter(username=username).exists():
            erro = "Esse nome de usuário já está em uso."

        else:

            try:

                validate_password(senha)

                with transaction.atomic():

                    conta = User.objects.create_user(
                        username=username,
                        email=email,
                        password=senha,
                    )

                    Usuario.objects.create(
                        usuario_login=conta,
                        nome=nome,
                        email=email,
                        setor=setor,
                        perfil=perfil,
                        tecnico=(perfil == "TECNICO"),
                        ativo=True
                    )

                return redirect("lista_usuarios")

            except ValidationError as e:

                erros_senha = e.messages

            except IntegrityError:

                erro = "Não foi possível cadastrar. Verifique os dados."

        return render(
            request,
            "chamados/cadastrar_usuario.html",
            {
                "setores": setores,
                "perfis": Usuario.PERFIL_CHOICES,
                "erro": erro,
                "erros_senha": erros_senha,
                "dados": request.POST,
            },
        )

    return render(
        request,
        "chamados/cadastrar_usuario.html",
        {
            "setores": setores,
            "perfis": Usuario.PERFIL_CHOICES,
        },
    )


# =====================================================
# EDITAR USUÁRIO
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR")
def editar_usuario(request, id):

    usuario = get_object_or_404(Usuario, id=id)

    setores = Setor.objects.all().order_by("nome")

    if request.method == "POST":

        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        setor_id = request.POST.get("setor")
        perfil = request.POST.get("perfil")

        perfis_validos = [
            "ADMINISTRADOR",
            "TECNICO",
            "SOLICITANTE",
        ]

        erro = None

        setor = Setor.objects.filter(id=setor_id).first()

        if not all([nome, email, setor_id, perfil]):

            erro = "Preencha todos os campos."

        elif perfil not in perfis_validos:

            erro = "Selecione um perfil válido."

        elif setor is None:

            erro = "Selecione um setor válido."

        else:

            usuario.nome = nome
            usuario.email = email
            usuario.setor = setor
            usuario.perfil = perfil
            usuario.tecnico = (perfil == "TECNICO")

            usuario.save()

            if usuario.usuario_login:

                usuario.usuario_login.email = email
                usuario.usuario_login.save()

            return redirect("lista_usuarios")

        return render(
            request,
            "chamados/editar_usuario.html",
            {
                "usuario": usuario,
                "setores": setores,
                "perfis": Usuario.PERFIL_CHOICES,
                "erro": erro,
            },
        )

    return render(
        request,
        "chamados/editar_usuario.html",
        {
            "usuario": usuario,
            "setores": setores,
            "perfis": Usuario.PERFIL_CHOICES,
        },
    )


# =====================================================
# ATIVAR / DESATIVAR USUÁRIO
# =====================================================

@login_required
@perfil_requerido("ADMINISTRADOR")
def alterar_ativo_usuario(request, id):

    if request.method != "POST":
        return redirect("lista_usuarios")

    usuario = get_object_or_404(Usuario, id=id)

    if usuario.usuario_login == request.user:
        return redirect("lista_usuarios")

    usuario.ativo = not usuario.ativo
    usuario.save()

    if usuario.usuario_login:

        usuario.usuario_login.is_active = usuario.ativo
        usuario.usuario_login.save()

    return redirect("lista_usuarios")

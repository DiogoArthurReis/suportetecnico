
from django.contrib import admin
from django.urls import path

from app.views import (
    dashboard,
    lista_chamados,
    detalhe_chamado,
    atribuir_tecnico,
    alterar_status,
    adicionar_resposta,
    solicitar_reabertura,
    abrir_chamado,
    login_usuario,
    logout_usuario,
    lista_usuarios,
    cadastrar_usuario,
    editar_usuario,
    alterar_ativo_usuario,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("chamados/", lista_chamados, name="lista_chamados"),
    path("chamados/<int:id>/", detalhe_chamado, name="detalhe_chamado"),
    path("chamados/<int:id>/atribuir-tecnico/", atribuir_tecnico, name="atribuir_tecnico"),
    path("chamados/<int:id>/alterar-status/", alterar_status, name="alterar_status"),
    path("chamados/<int:id>/responder/", adicionar_resposta, name="adicionar_resposta"),
    path("chamados/<int:id>/solicitar-reabertura/", solicitar_reabertura, name="solicitar_reabertura"),
    path("chamados/abrir/", abrir_chamado, name="abrir_chamado"),
    path("login/", login_usuario, name="login"),
    path("logout/", logout_usuario, name="logout"),
    path("usuarios/", lista_usuarios, name="lista_usuarios"),
    path("usuarios/cadastrar/", cadastrar_usuario, name="cadastrar_usuario"),
    path("usuarios/<int:id>/editar/", editar_usuario, name="editar_usuario"),
    path("usuarios/<int:id>/alterar-ativo/", alterar_ativo_usuario, name="alterar_ativo_usuario"),
]

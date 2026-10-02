from django.contrib import admin
from django.urls import path
from app.views import dashboard, lista_chamados, detalhe_chamado, atribuir_tecnico, alterar_status, adicionar_resposta, abrir_chamado

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("chamados/", lista_chamados, name="lista_chamados"),
    path("chamados/<int:id>/", detalhe_chamado, name="detalhe_chamado"),
    path("chamados/<int:id>/atribuir-tecnico/", atribuir_tecnico, name="atribuir_tecnico"),
    path("chamados/<int:id>/alterar-status/", alterar_status, name="alterar_status"),
    path("chamados/<int:id>/responder/", adicionar_resposta, name="adicionar_resposta"),
    path("chamados/abrir/", abrir_chamado, name="abrir_chamado"),
]
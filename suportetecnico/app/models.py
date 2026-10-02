from django.db import models
from django.contrib.auth.models import User

class Setor(models.Model):
    nome =  models.CharField(max_length=100, verbose_name="Nome do Setor")
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    usuario_login = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuário de login"
)
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

class Usuario(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    email = models.CharField(max_length=100, verbose_name="Email")
    setor = models.ForeignKey(
        Setor,
        on_delete=models.CASCADE,
        verbose_name="Setor"
    )
    tecnico = models.BooleanField(default=False, verbose_name="É técnico?")
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class Chamado(models.Model):
    PRIORIDADE_CHOICES = [
            ("BAIXA", "Baixa"),
            ("MEDIA", "Média"),
            ("ALTA", "Alta"),
            ("URGENTE", "Urgente"),
        ]

    STATUS_CHOICES = [
            ("ABERTO", "Aberto"),
            ("EM_ATENDIMENTO", "Em atendimento"),
            ("ENCERRADO", "Encerrado"),
            ("REABERTO", "Reaberto"),
        ]

    titulo = models.CharField(
            max_length=150,
            verbose_name="Título"
        )

    descricao = models.TextField(
            verbose_name="Descrição"
        )

    solicitante = models.ForeignKey(
            Usuario,
            on_delete=models.CASCADE,
            related_name="chamados_abertos",
            verbose_name="Solicitante"
        )

    setor = models.ForeignKey(
            Setor,
            on_delete=models.CASCADE,
            verbose_name="Setor"
        )

    categoria = models.ForeignKey(
            Categoria,
            on_delete=models.CASCADE,
            verbose_name="Categoria"
        )

    tecnico = models.ForeignKey(
            Usuario,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="chamados_atendidos",
            verbose_name="Técnico responsável"
        )

    prioridade = models.CharField(
            max_length=20,
            choices=PRIORIDADE_CHOICES,
            default="MEDIA",
            verbose_name="Prioridade"
        )

    status = models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default="ABERTO",
            verbose_name="Status"
        )

    data_abertura = models.DateTimeField(
            auto_now_add=True,
            verbose_name="Data de abertura"
        )

    data_inicio = models.DateTimeField(
            null=True,
            blank=True,
            verbose_name="Data de início"
        )

    data_encerramento = models.DateTimeField(
            null=True,
            blank=True,
            verbose_name="Data de encerramento"
        )

    def __str__(self):
            return self.titulo

    class Meta:
            verbose_name = "Chamado"
            verbose_name_plural = "Chamados"

class Resposta(models.Model):
    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name="respostas",
        verbose_name="Chamado"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )

    mensagem = models.TextField(
        verbose_name="Mensagem"
    )

    data = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da resposta"
    )

    def __str__(self):
        return f"Resposta - {self.chamado}"

    class Meta:
        verbose_name = "Resposta"
        verbose_name_plural = "Respostas"
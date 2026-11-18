from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Artigo


class ArtigoForm(forms.ModelForm):

    conteudo = forms.CharField(
        widget=CKEditor5Widget(
            config_name="default"
        )
    )

    class Meta:
        model = Artigo
        fields = [
            "titulo",
            "categoria",
            "conteudo",
            "publicado",
        ]
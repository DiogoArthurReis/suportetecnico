from django import template
from django.utils.html import strip_tags
from html import unescape

register = template.Library()

@register.filter
def resumo_artigo(conteudo):

    texto = unescape(conteudo)

    texto = texto.replace("</p>", " ")
    texto = texto.replace("<br>", " ")
    texto = texto.replace("<br/>", " ")
    texto = texto.replace("<br />", " ")

    texto = strip_tags(texto)

    texto = texto.replace("\xa0", " ")

    texto = " ".join(texto.split())

    return texto
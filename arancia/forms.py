from datetime import datetime
from django import forms

class RomaneioForm(forms.Form):
    nome_formulario = 'Criar Romaneio'
    serial = forms.CharField(label='Serial', max_length=50,)
    chamado = forms.CharField(label='Chamado', max_length=50)
    usuario = forms.CharField(label='Usuário', max_length=50)
    filial = forms.CharField(label='Filial', max_length=50)
    destino = forms.CharField(label='Destino', max_length=50)

class RevisarForm(forms.Form):
    nome_formulario = 'Revisar Romaneio'
    numero_romaneio = forms.CharField(label='Número do Romaneio', max_length=11)

class DespachoForm(forms.Form):
    nome_formulario = 'Despacho Romaneio'
    usuario = forms.CharField(label='Usuário', max_length=50)
    filial = forms.CharField(label='Filial', max_length=50)
    romaneio = forms.CharField(label='Romaneio', max_length=11)
    codigo_interno = forms.CharField(label='Código Interno', max_length=50)
    canal_parceiro = forms.CharField(label='Canal Parceiro', max_length=50)
    codigo_parceiro = forms.CharField(label='Código Parceiro', max_length=50)

class RastreioForm(forms.Form):
    nome_formulario = 'Rastreio Romaneio'
    numero_romaneio = forms.CharField(label='Número do Romaneio', max_length=11)

class DadosRastreioForm(forms.Form):
    nome_formulario = 'Dados Rastreio'
    data = forms.DateTimeField(label='Data')
    hora = forms.DateTimeField(label='Hora')
    usuario = forms.CharField(label='Usuário', max_length=50)
    filial = forms.CharField(label='Filial', max_length=50)
    rastreio_interno = forms.CharField(label='Rastreio Interno', max_length=50)
    rastrieo_parceiro = forms.CharField(label='Rastreio Empresa', max_length=50)
    canal = forms.CharField(label='Canal Parceiro', max_length=50)

class EntregaPaecForm(forms.Form):
    nome_formulario = 'Entrega PAEC'
    serial = forms.CharField(label='Serial', max_length=50)
    chip = forms.CharField(label='Chip', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)
    data = forms.DateTimeField(label='Data')
    tecnico = forms.CharField(label='Técnico', max_length=50)

class EntregaPicpacForm(forms.Form):
    nome_formulario = 'Entrega PicPac'
    serial = forms.CharField(label='Serial', max_length=50)
    chip = forms.CharField(label='Chip', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)
    data = forms.DateTimeField(label='Data')
    tecnico = forms.CharField(label='Técnico', max_length=50)

class EstornoPaecForm(forms.Form):
    nome_formulario = 'Estorno PAEC'
    serial = forms.CharField(label='Serial', max_length=50)

class EstornoPicpacForm(forms.Form):
    nome_formulario = 'Estorno PicPac'
    serial = forms.CharField(label='Serial', max_length=50)

class EstornoRomaneioForm(forms.Form):
    nome_formulario = 'Estorno Romaneio'
    romaneio = forms.CharField(label='Número do romaneio', max_length=11)

class ConsultaForm(forms.Form):
    nome_formulario = 'Consulta de ID'
    id = forms.CharField(label='Insira o ID:', max_length=20)

class PreRecebimentoForm(forms.Form):
    nome_formulario = 'Pré-Recebimento'
    serial = forms.CharField(label='Serial', max_length=50)
    id = forms.CharField(label='ID', max_length=50)
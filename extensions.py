from db import Database
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from urllib.parse import urlencode
from starlette.routing import NoMatchFound
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

db = Database()

ROUTE_NAMES = {
    'auth.login': 'login', 'auth.logout': 'logout',
    'auth.recuperar_senha': 'recuperar_senha', 'auth.index': 'index',
    'dashboard.dashboard': 'dashboard',
    'dashboard.realizar_consulta': 'realizar_consulta',
    'dashboard.cancelar_consulta': 'cancelar_consulta',
    'clientes.clientes': 'clientes', 'clientes.novo_cliente': 'novo_cliente',
    'clientes.editar_cliente': 'editar_cliente',
    'clientes.excluir_cliente': 'excluir_cliente',
    'dentistas.dentistas': 'dentistas',
    'dentistas.novo_dentista': 'novo_dentista',
    'dentistas.reativar_dentista': 'reativar_dentista',
    'dentistas.editar_dentista': 'editar_dentista',
    'dentistas.excluir_dentista': 'excluir_dentista',
    'agendamentos.agendamentos': 'agendamentos',
    'agendamentos.novo_agendamento': 'novo_agendamento',
    'agendamentos.prontuario': 'prontuario',
    'agendamentos.agenda_dentista': 'agenda_dentista',
    'agendar_online.agendar_online': 'agendar_online',
    'agendar_online.buscar_horarios': 'buscar_horarios',
    'agendar_online.salvar_agendamento_online': 'salvar_agendamento_online',
    'agendar_online.compartilhar_link': 'compartilhar_link',
    'agendar_online.gerar_qrcode': 'gerar_qrcode',
    'relatorios.relatorios': 'relatorios',
    'relatorios.api_relatorios_dados': 'api_relatorios_dados',
    'relatorios.exportar_relatorio': 'exportar_relatorio',
    'relatorios.relatorios_imprimir': 'relatorios_imprimir',
    'configuracoes.configuracoes': 'configuracoes',
    'configuracoes.trocar_senha': 'trocar_senha',
    'configuracoes.criar_usuario': 'criar_usuario',
    'configuracoes.editar_usuario': 'editar_usuario',
    'configuracoes.excluir_usuario': 'excluir_usuario',
}

def login_required(request):
    if 'usuario_id' not in request.session:
        raise HTTPException(status_code=303, headers={'Location': '/login'})
    return True

PATH_PARAM_ROUTES = {
    'realizar_consulta': ['consulta_id'],
    'cancelar_consulta': ['consulta_id'],
    'editar_cliente': ['cliente_id'],
    'excluir_cliente': ['cliente_id'],
    'reativar_dentista': ['dentista_id'],
    'editar_dentista': ['dentista_id'],
    'excluir_dentista': ['dentista_id'],
    'prontuario': ['paciente_id'],
    'agenda_dentista': ['dentista_id'],
    'editar_usuario': ['user_id'],
    'excluir_usuario': ['user_id'],
    'gerar_qrcode': ['path'],
}

def template_url_for(request, name, **params):
    if name == 'static':
        return request.url_for('static', path=params.get('filename', '')).path
    actual = ROUTE_NAMES.get(name, name)
    path_params = PATH_PARAM_ROUTES.get(actual, [])
    url_params = {}
    query_params = {}
    for k, v in params.items():
        if k in path_params:
            url_params[k] = v
        else:
            query_params[k] = v
    try:
        url = request.url_for(actual, **url_params).path
    except NoMatchFound:
        try:
            url = request.url_for(actual).path
        except NoMatchFound:
            url = '/' + actual.replace('_', '-')
        query_params.update(url_params)
    if query_params:
        url += '?' + urlencode(query_params)
    return url

def render(request, template_name, **context):
    context['session'] = request.session
    context['url_for'] = lambda name, **params: template_url_for(request, name, **params)
    return templates.TemplateResponse(request, template_name, context)

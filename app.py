from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import timedelta
from extensions import db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = FastAPI(title="Clínica Odontológica Sorriso Saudável")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code in (301, 302, 303, 307, 308):
        location = exc.headers.get('Location') if exc.headers else None
        if location:
            return RedirectResponse(url=location, status_code=exc.status_code)
    return JSONResponse(
        {'detail': exc.detail},
        status_code=exc.status_code,
        headers=exc.headers
    )

app.add_middleware(
    SessionMiddleware,
    secret_key='clinica_odontologica_secret_key_2024',
    max_age=int(timedelta(hours=8).total_seconds()),
    same_site='lax',
    https_only=False
)

from modulos.auth import auth_router
from modulos.dashboard import dashboard_router
from modulos.clientes import clientes_router
from modulos.dentistas import dentistas_router
from modulos.agendamentos import agendamentos_router
from modulos.agendar_online import agendar_online_router
from modulos.relatorios import relatorios_router
from modulos.configuracoes import configuracoes_router

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(clientes_router)
app.include_router(dentistas_router)
app.include_router(agendamentos_router)
app.include_router(agendar_online_router)
app.include_router(relatorios_router)
app.include_router(configuracoes_router)

@app.get('/enviar-lembretes')
def enviar_lembretes():
    from enviar_lembretes import enviar_todos_lembretes
    import io, sys, json
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        enviar_todos_lembretes()
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
    return {'output': output}

from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
import hashlib
import random
import string

from extensions import db, render

auth_router = APIRouter()

@auth_router.get('/', name='index')
def index(request: Request):
    request.session.clear()
    return RedirectResponse(url=str(request.url_for('login')), status_code=303)

@auth_router.get('/login', name='login')
def login_get(request: Request):
    if 'usuario_id' in request.session:
        request.session.clear()
    return render(request, 'login.html')

@auth_router.post('/login', name='login_post')
async def login_post(request: Request):
    form = await request.form()
    username = form['username']
    senha = hashlib.sha256(form['senha'].encode()).hexdigest()

    db.cursor.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ? AND ativo = 1', (username, senha))
    usuario = db.cursor.fetchone()

    if usuario:
        request.session.clear()
        request.session['usuario_id'] = usuario[0]
        request.session['usuario_nome'] = usuario[4]
        request.session['usuario_tipo'] = usuario[3]
        return RedirectResponse(url=str(request.url_for('dashboard')), status_code=303)
    else:
        return render(request, 'login.html', erro='Usuário ou senha inválidos')

@auth_router.get('/logout', name='logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url=str(request.url_for('login')), status_code=303)

@auth_router.post('/recuperar-senha', name='recuperar_senha')
async def recuperar_senha(request: Request):
    form = await request.form()
    contato = form.get('contato')

    db.cursor.execute('''
        SELECT id, username, nome_completo, email, celular FROM usuarios
        WHERE email = ? OR celular = ? OR username = ?
    ''', (contato, contato, contato))
    usuario = db.cursor.fetchone()

    if not usuario:
        return render(request, 'login.html', erro='Email, celular ou usuário não encontrado!')

    nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()

    db.cursor.execute('UPDATE usuarios SET senha = ? WHERE id = ?', (nova_senha_hash, usuario[0]))
    db.conn.commit()

    return render(request, 'login.html', msg=f'Usuário: {usuario[1]} - Nova senha: {nova_senha}')

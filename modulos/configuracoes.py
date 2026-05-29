from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from urllib.parse import quote
import hashlib

from extensions import db, login_required, render

configuracoes_router = APIRouter()

@configuracoes_router.get('/configuracoes', name='configuracoes')
def configuracoes(request: Request):
    login_required(request)
    if request.session.get('usuario_tipo') == 'admin':
        db.cursor.execute('SELECT id, username, tipo, nome_completo, email, celular, ativo FROM usuarios')
        usuarios = db.cursor.fetchall()
    else:
        usuarios = []
    return render(request, 'configuracoes.html', usuarios=usuarios)

@configuracoes_router.post('/configuracoes/trocar-senha', name='trocar_senha')
async def trocar_senha(request: Request):
    login_required(request)
    form = await request.form()
    senha_atual = form.get('senha_atual')
    nova_senha = form.get('nova_senha')
    confirmar = form.get('confirmar_senha')

    if nova_senha != confirmar:
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Senhas não coincidem')
        return RedirectResponse(url=url, status_code=303)

    senha_hash = hashlib.sha256(senha_atual.encode()).hexdigest()
    db.cursor.execute('SELECT id FROM usuarios WHERE id = ? AND senha = ?', (request.session['usuario_id'], senha_hash))
    if not db.cursor.fetchone():
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Senha atual incorreta')
        return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('UPDATE usuarios SET senha = ? WHERE id = ?', (hashlib.sha256(nova_senha.encode()).hexdigest(), request.session['usuario_id']))
    db.conn.commit()
    return RedirectResponse(url=str(request.url_for('configuracoes')), status_code=303)

@configuracoes_router.post('/configuracoes/criar-usuario', name='criar_usuario')
async def criar_usuario(request: Request):
    login_required(request)
    if request.session.get('usuario_tipo') != 'admin':
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Apenas admin')
        return RedirectResponse(url=url, status_code=303)

    form = await request.form()
    username = form.get('username')
    senha = form.get('senha')
    nome = form.get('nome_completo')
    tipo = form.get('tipo')

    db.cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
    if db.cursor.fetchone():
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Usuário já existe')
        return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('INSERT INTO usuarios (username, senha, tipo, nome_completo, ativo) VALUES (?, ?, ?, ?, 1)',
                     (username, hashlib.sha256(senha.encode()).hexdigest(), tipo, nome))
    db.conn.commit()
    return RedirectResponse(url=str(request.url_for('configuracoes')), status_code=303)

@configuracoes_router.post('/configuracoes/editar-usuario/{user_id}', name='editar_usuario')
async def editar_usuario(request: Request, user_id: int):
    login_required(request)
    if request.session.get('usuario_tipo') != 'admin':
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Apenas admin')
        return RedirectResponse(url=url, status_code=303)

    form = await request.form()
    username = form.get('username')
    nome = form.get('nome_completo')
    tipo = form.get('tipo')
    ativo = 1 if form.get('ativo') == 'on' else 0

    db.cursor.execute('SELECT id FROM usuarios WHERE username = ? AND id != ?', (username, user_id))
    if db.cursor.fetchone():
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Nome de usuario ja existe')
        return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('UPDATE usuarios SET username = ?, nome_completo = ?, tipo = ?, ativo = ? WHERE id = ?',
                      (username, nome, tipo, ativo, user_id))
    db.conn.commit()
    return RedirectResponse(url=str(request.url_for('configuracoes')), status_code=303)

@configuracoes_router.get('/configuracoes/excluir-usuario/{user_id}', name='excluir_usuario')
def excluir_usuario(request: Request, user_id: int):
    login_required(request)
    if request.session.get('usuario_tipo') != 'admin':
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Apenas admin')
        return RedirectResponse(url=url, status_code=303)
    if user_id == request.session['usuario_id']:
        url = str(request.url_for('configuracoes')) + '?erro=' + quote('Não pode excluir a si mesmo')
        return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
    db.conn.commit()
    return RedirectResponse(url=str(request.url_for('configuracoes')), status_code=303)

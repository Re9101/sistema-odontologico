from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from urllib.parse import quote

from extensions import db, login_required, render

clientes_router = APIRouter()

@clientes_router.get('/clientes', name='clientes')
def clientes(request: Request):
    login_required(request)
    db.cursor.execute('SELECT * FROM pacientes ORDER BY nome ASC')
    clientes_lista = db.cursor.fetchall()
    return render(request, 'clientes.html', clientes=clientes_lista)

@clientes_router.post('/clientes/novo', name='novo_cliente')
async def novo_cliente(request: Request):
    login_required(request)
    form = await request.form()
    nome = form.get('nome', '')
    telefone = form.get('telefone', '')
    email = form.get('email', '')
    data_nascimento = form.get('data_nascimento', '')
    convenio = form.get('convenio', '')
    alergias = form.get('alergias', '')

    db.cursor.execute('''
        INSERT INTO pacientes (nome, telefone, email, data_nascimento, convenio, alergias)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, telefone, email, data_nascimento, convenio, alergias))
    db.conn.commit()

    return RedirectResponse(url=str(request.url_for('clientes')), status_code=303)

@clientes_router.post('/clientes/editar/{cliente_id}', name='editar_cliente')
async def editar_cliente(request: Request, cliente_id: int):
    login_required(request)
    form = await request.form()
    nome = form.get('nome')
    telefone = form.get('telefone')
    email = form.get('email')
    data_nascimento = form.get('data_nascimento')
    convenio = form.get('convenio')
    alergias = form.get('alergias')

    db.cursor.execute('''
        UPDATE pacientes
        SET nome = ?, telefone = ?, email = ?, data_nascimento = ?, convenio = ?, alergias = ?
        WHERE id = ?
    ''', (nome, telefone, email, data_nascimento, convenio, alergias, cliente_id))
    db.conn.commit()

    return RedirectResponse(url=str(request.url_for('clientes')), status_code=303)

@clientes_router.get('/clientes/excluir/{cliente_id}', name='excluir_cliente')
def excluir_cliente(request: Request, cliente_id: int):
    login_required(request)
    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE paciente_id = ?', (cliente_id,))
    tem_consultas = db.cursor.fetchone()[0]

    if tem_consultas > 0:
        url = str(request.url_for('clientes')) + '?erro=' + quote('Não é possível excluir cliente com consultas agendadas!')
        return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('DELETE FROM pacientes WHERE id = ?', (cliente_id,))
    db.conn.commit()

    url = str(request.url_for('clientes')) + '?msg=' + quote('Cliente excluído com sucesso!')
    return RedirectResponse(url=url, status_code=303)

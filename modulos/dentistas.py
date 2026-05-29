from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from urllib.parse import quote

from extensions import db, login_required, render

dentistas_router = APIRouter()

@dentistas_router.get('/dentistas', name='dentistas')
def dentistas(request: Request):
    login_required(request)
    db.cursor.execute('SELECT * FROM dentistas WHERE ativo = 1 ORDER BY nome')
    lista_dentistas = db.cursor.fetchall()
    return render(request, 'dentistas.html', dentistas=lista_dentistas)

@dentistas_router.post('/dentistas/novo', name='novo_dentista')
async def novo_dentista(request: Request):
    login_required(request)
    form = await request.form()
    nome = form.get('nome')
    cro = form.get('cro')
    especialidade = form.get('especialidade')
    telefone = form.get('telefone')
    email = form.get('email')

    db.cursor.execute('SELECT id, ativo FROM dentistas WHERE cro = ?', (cro,))
    resultado = db.cursor.fetchone()

    if resultado:
        if resultado[1] == 1:
            url = str(request.url_for('dentistas')) + '?erro=' + quote('CRO já cadastrado em um dentista ATIVO!')
            return RedirectResponse(url=url, status_code=303)
        else:
            db.cursor.execute('''
                UPDATE dentistas
                SET nome = ?, especialidade = ?, telefone = ?, email = ?, ativo = 1
                WHERE cro = ?
            ''', (nome, especialidade, telefone, email, cro))
            db.conn.commit()
            url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista reativado com sucesso!')
            return RedirectResponse(url=url, status_code=303)

    db.cursor.execute('''
        INSERT INTO dentistas (nome, cro, especialidade, telefone, email, ativo)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (nome, cro, especialidade, telefone, email))
    db.conn.commit()

    url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista cadastrado com sucesso!')
    return RedirectResponse(url=url, status_code=303)

@dentistas_router.get('/dentistas/reativar/{dentista_id}', name='reativar_dentista')
def reativar_dentista(request: Request, dentista_id: int):
    login_required(request)
    try:
        db.cursor.execute('UPDATE dentistas SET ativo = 1 WHERE id = ?', (dentista_id,))
        db.conn.commit()
        url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista reativado com sucesso!')
        return RedirectResponse(url=url, status_code=303)
    except Exception as e:
        url = str(request.url_for('dentistas')) + '?erro=' + quote(f'Erro ao reativar: {e}')
        return RedirectResponse(url=url, status_code=303)

@dentistas_router.post('/dentistas/editar/{dentista_id}', name='editar_dentista')
async def editar_dentista(request: Request, dentista_id: int):
    login_required(request)
    form = await request.form()
    nome = form.get('nome')
    cro = form.get('cro')
    especialidade = form.get('especialidade')
    telefone = form.get('telefone')
    email = form.get('email')

    try:
        db.cursor.execute('''
            UPDATE dentistas
            SET nome = ?, cro = ?, especialidade = ?, telefone = ?, email = ?
            WHERE id = ?
        ''', (nome, cro, especialidade, telefone, email, dentista_id))
        db.conn.commit()
        url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista atualizado com sucesso!')
        return RedirectResponse(url=url, status_code=303)
    except Exception as e:
        print(f"Erro: {e}")
        url = str(request.url_for('dentistas')) + '?erro=' + quote(f'Erro ao atualizar: {e}')
        return RedirectResponse(url=url, status_code=303)

@dentistas_router.get('/dentistas/excluir/{dentista_id}', name='excluir_dentista')
def excluir_dentista(request: Request, dentista_id: int):
    login_required(request)
    try:
        db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE dentista_id = ?', (dentista_id,))
        tem_consultas = db.cursor.fetchone()[0]

        if tem_consultas > 0:
            db.cursor.execute('UPDATE dentistas SET ativo = 0 WHERE id = ?', (dentista_id,))
            db.conn.commit()
            url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista desativado (possui consultas vinculadas)')
            return RedirectResponse(url=url, status_code=303)
        else:
            db.cursor.execute('DELETE FROM dentistas WHERE id = ?', (dentista_id,))
            db.conn.commit()
            url = str(request.url_for('dentistas')) + '?msg=' + quote('Dentista excluído com sucesso!')
            return RedirectResponse(url=url, status_code=303)
    except Exception as e:
        print(f"Erro: {e}")
        url = str(request.url_for('dentistas')) + '?erro=' + quote(f'Erro ao excluir: {e}')
        return RedirectResponse(url=url, status_code=303)

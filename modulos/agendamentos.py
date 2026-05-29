from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from datetime import date, datetime, timedelta
from urllib.parse import quote

from extensions import db, login_required, render

agendamentos_router = APIRouter()

@agendamentos_router.get('/agendamentos', name='agendamentos')
def agendamentos(request: Request):
    login_required(request)
    data_filtro = request.query_params.get('data', date.today().isoformat())

    data_atual_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
    proximo_dia_anterior = (data_atual_obj - timedelta(days=1)).isoformat()
    proximo_dia_posterior = (data_atual_obj + timedelta(days=1)).isoformat()

    db.cursor.execute('''
        SELECT c.id, c.nome_paciente, c.data_hora, c.dente_regiao, c.status,
               d.nome as nome_dentista
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE date(c.data_hora) = ? AND c.status = 'agendada'
        ORDER BY c.data_hora ASC
    ''', (data_filtro,))

    consultas = db.cursor.fetchall()

    db.cursor.execute('SELECT id, nome, especialidade FROM dentistas WHERE ativo = 1')
    dentistas_lista = db.cursor.fetchall()

    return render(request, 'agendamentos.html',
                  consultas=consultas,
                  dentistas=dentistas_lista,
                  data_atual=data_filtro,
                  proximo_dia_anterior=proximo_dia_anterior,
                  proximo_dia_posterior=proximo_dia_posterior)

@agendamentos_router.post('/agendamentos/novo', name='novo_agendamento')
async def novo_agendamento(request: Request):
    login_required(request)
    form = await request.form()
    nome_paciente = form.get('nome_paciente')
    dentista_id = form.get('dentista_id')
    data = form.get('data')
    hora = form.get('hora')
    dente_regiao = form.get('dente_regiao', '')

    if not nome_paciente or not dentista_id or not data or not hora:
        url = str(request.url_for('agendamentos')) + '?data=' + data + '&erro=' + quote('Preencha todos os campos!')
        return RedirectResponse(url=url, status_code=303)

    data_hora = f"{data} {hora}:00"

    db.cursor.execute('SELECT id FROM pacientes WHERE nome = ?', (nome_paciente,))
    paciente = db.cursor.fetchone()
    paciente_id = paciente[0] if paciente else None

    db.cursor.execute('''
        INSERT INTO consultas (nome_paciente, paciente_id, dentista_id, data_hora, dente_regiao, status)
        VALUES (?, ?, ?, ?, ?, 'agendada')
    ''', (nome_paciente, paciente_id, dentista_id, data_hora, dente_regiao))
    db.conn.commit()

    url = str(request.url_for('agendamentos')) + '?data=' + data + '&msg=' + quote('Consulta agendada com sucesso!')
    return RedirectResponse(url=url, status_code=303)

@agendamentos_router.get('/prontuario/{paciente_id}', name='prontuario')
def prontuario(request: Request, paciente_id: int):
    login_required(request)
    db.cursor.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,))
    paciente = db.cursor.fetchone()

    if not paciente:
        return "Paciente não encontrado", 404

    db.cursor.execute('''
        SELECT c.*, d.nome as dentista_nome
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE c.paciente_id = ?
        ORDER BY c.data_hora DESC
    ''', (paciente_id,))
    consultas = db.cursor.fetchall()

    return render(request, 'prontuario.html', paciente=paciente, consultas=consultas)

@agendamentos_router.get('/agenda/dentista/{dentista_id}', name='agenda_dentista')
def agenda_dentista(request: Request, dentista_id: int):
    login_required(request)
    db.cursor.execute('''
        SELECT c.*
        FROM consultas c
        WHERE c.dentista_id = ? AND date(c.data_hora) >= date('now')
        ORDER BY c.data_hora
    ''', (dentista_id,))
    consultas = db.cursor.fetchall()
    return render(request, 'agenda_dentista.html', consultas=consultas)

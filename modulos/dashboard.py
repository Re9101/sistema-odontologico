from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from datetime import date, timedelta

from extensions import db, login_required, render

dashboard_router = APIRouter()

@dashboard_router.get('/dashboard', name='dashboard')
def dashboard(request: Request):
    login_required(request)
    hoje = date.today().isoformat()

    db.cursor.execute('SELECT COUNT(*) FROM pacientes')
    total_pacientes = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE date(data_hora) = ? AND status = "agendada"', (hoje,))
    consultas_hoje = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE status = "agendada"')
    consultas_agendadas = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM dentistas WHERE ativo = 1')
    total_dentistas = db.cursor.fetchone()[0]

    db.cursor.execute('''
        SELECT COUNT(DISTINCT dentista_id) FROM consultas
        WHERE date(data_hora) = date('now') AND status = 'agendada'
    ''')
    dentistas_com_consulta = db.cursor.fetchone()[0] or 0
    taxa_ocupacao = round((dentistas_com_consulta / total_dentistas) * 100) if total_dentistas > 0 else 0

    trinta_dias_atras = date.today() - timedelta(days=30)
    sessenta_dias_atras = date.today() - timedelta(days=60)

    db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE date(data_cadastro) >= ?', (trinta_dias_atras,))
    novos_pacientes_30 = db.cursor.fetchone()[0] or 1

    db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE date(data_cadastro) BETWEEN ? AND ?', (sessenta_dias_atras, trinta_dias_atras))
    novos_pacientes_anterior = db.cursor.fetchone()[0] or 1

    crescimento_pacientes = round(((novos_pacientes_30 - novos_pacientes_anterior) / novos_pacientes_anterior) * 100)

    db.cursor.execute('''
        SELECT
            COUNT(CASE WHEN status = 'cancelada' THEN 1 END) as canceladas,
            COUNT(*) as total
        FROM consultas
        WHERE date(created_at) >= ?
    ''', (trinta_dias_atras,))
    resultado = db.cursor.fetchone()
    canceladas = resultado[0] or 0
    total_consultas = resultado[1] or 1
    taxa_cancelamento = round((canceladas / total_consultas) * 100)

    db.cursor.execute('''
        SELECT c.id, c.data_hora, c.nome_paciente, d.nome as dentista_nome
        FROM consultas c
        JOIN dentistas d ON c.dentista_id = d.id
        WHERE date(c.data_hora) = date('now') AND c.status = 'agendada'
        ORDER BY c.data_hora ASC
    ''')
    consultas_raw = db.cursor.fetchall()

    proximas_consultas = []
    for c in consultas_raw:
        data_parte = c[1].split()[0]
        hora_parte = c[1].split()[1][:5]
        proximas_consultas.append({
            'id': c[0],
            'data_hora': c[1],
            'paciente_nome': c[2],
            'dentista_nome': c[3],
            'data': data_parte,
            'hora': hora_parte
        })

    return render(request, 'dashboard.html',
                  total_pacientes=total_pacientes,
                  consultas_hoje=consultas_hoje,
                  consultas_agendadas=consultas_agendadas,
                  total_dentistas=total_dentistas,
                  proximas_consultas=proximas_consultas,
                  data_atual=hoje,
                  taxa_ocupacao=taxa_ocupacao,
                  crescimento_pacientes=crescimento_pacientes,
                  taxa_cancelamento=taxa_cancelamento)

@dashboard_router.get('/consulta/realizar/{consulta_id}', name='realizar_consulta')
def realizar_consulta(request: Request, consulta_id: int):
    login_required(request)
    try:
        db.cursor.execute('UPDATE consultas SET status = "realizada" WHERE id = ?', (consulta_id,))
        db.conn.commit()
        url = str(request.url_for('agendamentos')) + '?msg=Consulta+realizada+com+sucesso!'
        return RedirectResponse(url=url, status_code=303)
    except Exception as e:
        print(f"Erro: {e}")
        url = str(request.url_for('agendamentos')) + '?erro=Erro+ao+realizar+consulta'
        return RedirectResponse(url=url, status_code=303)

@dashboard_router.get('/consulta/cancelar/{consulta_id}', name='cancelar_consulta')
def cancelar_consulta(request: Request, consulta_id: int):
    login_required(request)
    try:
        db.cursor.execute('UPDATE consultas SET status = "cancelada" WHERE id = ?', (consulta_id,))
        db.conn.commit()
        url = str(request.url_for('agendamentos')) + '?msg=Consulta+cancelada!'
        return RedirectResponse(url=url, status_code=303)
    except Exception as e:
        print(f"Erro: {e}")
        url = str(request.url_for('agendamentos')) + '?erro=Erro+ao+cancelar+consulta'
        return RedirectResponse(url=url, status_code=303)

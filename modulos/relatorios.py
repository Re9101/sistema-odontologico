from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from datetime import datetime, timedelta
import io

from extensions import db, login_required, render

relatorios_router = APIRouter()

@relatorios_router.get('/relatorios', name='relatorios')
def relatorios(request: Request):
    login_required(request)
    return render(request, 'relatorios.html')

@relatorios_router.get('/api/relatorios/dados', name='api_relatorios_dados')
def api_relatorios_dados(request: Request):
    login_required(request)
    periodo = int(request.query_params.get('periodo', 30))
    data_inicio = request.query_params.get('data_inicio')
    data_fim = request.query_params.get('data_fim')

    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
    else:
        fim = datetime.now()
        inicio = fim - timedelta(days=periodo)

    db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE date(data_cadastro) BETWEEN date(?) AND date(?)', (inicio, fim))
    novos_pacientes = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE date(data_hora) BETWEEN date(?) AND date(?) AND status = "realizada"', (inicio, fim))
    consultas_realizadas = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE date(data_hora) BETWEEN date(?) AND date(?) AND status = "cancelada"', (inicio, fim))
    cancelamentos = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM dentistas WHERE ativo = 1')
    total_dentistas = db.cursor.fetchone()[0] or 1

    db.cursor.execute('SELECT COUNT(DISTINCT dentista_id) FROM consultas WHERE date(data_hora) = date("now")')
    dentistas_trabalhando = db.cursor.fetchone()[0] or 0
    taxa_ocupacao = round((dentistas_trabalhando / total_dentistas) * 100)

    periodo_anterior_inicio = inicio - timedelta(days=periodo)

    db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE date(data_cadastro) BETWEEN date(?) AND date(?)', (periodo_anterior_inicio, inicio))
    pacientes_anterior = db.cursor.fetchone()[0]
    crescimento_pacientes = round(((novos_pacientes - pacientes_anterior) / max(pacientes_anterior, 1)) * 100)

    db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE date(data_hora) BETWEEN date(?) AND date(?) AND status = "realizada"', (periodo_anterior_inicio, inicio))
    consultas_anterior = db.cursor.fetchone()[0]
    crescimento_consultas = round(((consultas_realizadas - consultas_anterior) / max(consultas_anterior, 1)) * 100)

    taxa_cancelamento = round((cancelamentos / max(consultas_realizadas + cancelamentos, 1)) * 100)

    dias = []
    pacientes_por_dia = []
    consultas_por_dia = []
    for i in range(min(periodo, 30)):
        dia = inicio + timedelta(days=i)
        if dia > fim:
            break
        dias.append(dia.strftime('%d/%m'))

        db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE date(data_cadastro) = ?', (dia,))
        pacientes_por_dia.append(db.cursor.fetchone()[0])

        db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE date(data_hora) = ? AND status = "realizada"', (dia,))
        consultas_por_dia.append(db.cursor.fetchone()[0])

    meses = []
    pacientes_por_mes = []
    consultas_por_mes = []
    for i in range(6):
        mes = fim.replace(day=1) - timedelta(days=30*i)
        meses.insert(0, mes.strftime('%b/%Y'))

        db.cursor.execute('SELECT COUNT(*) FROM pacientes WHERE strftime("%Y-%m", data_cadastro) = ?', (mes.strftime('%Y-%m'),))
        pacientes_por_mes.insert(0, db.cursor.fetchone()[0])

        db.cursor.execute('SELECT COUNT(*) FROM consultas WHERE strftime("%Y-%m", data_hora) = ? AND status = "realizada"', (mes.strftime('%Y-%m'),))
        consultas_por_mes.insert(0, db.cursor.fetchone()[0])

    db.cursor.execute('''
        SELECT d.nome, COUNT(c.id) as total
        FROM dentistas d
        LEFT JOIN consultas c ON c.dentista_id = d.id AND c.status = 'realizada'
        WHERE d.ativo = 1
        GROUP BY d.id
        ORDER BY total DESC
    ''')
    dentistas_data = db.cursor.fetchall()
    dentistas_nomes = [d[0] for d in dentistas_data] if dentistas_data else []
    dentistas_consultas = [d[1] for d in dentistas_data] if dentistas_data else []

    db.cursor.execute('''
        SELECT nome_paciente, COUNT(id) as total, MAX(date(data_hora)) as ultima
        FROM consultas
        WHERE status = 'realizada' AND nome_paciente IS NOT NULL
        GROUP BY nome_paciente
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_pacientes = [{'nome': row[0], 'total': row[1], 'ultima': row[2]} for row in db.cursor.fetchall()]

    return {
        'novos_pacientes': novos_pacientes,
        'consultas_realizadas': consultas_realizadas,
        'taxa_ocupacao': taxa_ocupacao,
        'cancelamentos': cancelamentos,
        'crescimento_pacientes': crescimento_pacientes,
        'crescimento_consultas': crescimento_consultas,
        'taxa_cancelamento': taxa_cancelamento,
        'dias': dias,
        'pacientes_por_dia': pacientes_por_dia,
        'consultas_por_dia': consultas_por_dia,
        'meses': meses,
        'pacientes_por_mes': pacientes_por_mes,
        'consultas_por_mes': consultas_por_mes,
        'dentistas_nomes': dentistas_nomes,
        'dentistas_consultas': dentistas_consultas,
        'top_pacientes': top_pacientes
    }

@relatorios_router.get('/relatorios/exportar', name='exportar_relatorio')
def exportar_relatorio(request: Request):
    login_required(request)
    periodo = request.query_params.get('periodo', 30)
    data_inicio = request.query_params.get('data_inicio')
    data_fim = request.query_params.get('data_fim')

    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
    else:
        fim = datetime.now()
        inicio = fim - timedelta(days=int(periodo))

    db.cursor.execute('''
        SELECT
            c.id,
            c.nome_paciente,
            d.nome as dentista_nome,
            c.data_hora,
            c.status,
            c.created_at
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE date(c.created_at) BETWEEN date(?) AND date(?)
        ORDER BY c.created_at DESC
    ''', (inicio, fim))

    consultas = db.cursor.fetchall()

    db.cursor.execute('''
        SELECT nome, telefone, email, data_cadastro
        FROM pacientes
        WHERE date(data_cadastro) BETWEEN date(?) AND date(?)
        ORDER BY data_cadastro DESC
    ''', (inicio, fim))

    pacientes = db.cursor.fetchall()

    html = f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório - Clínica Sorriso Saudável</title>
    </head>
    <body>
        <h2 style="color: #0077b6;">Clínica Sorriso Saudável</h2>
        <h3>Relatório de Consultas e Pacientes</h3>
        <p><strong>Período:</strong> {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}</p>
        <p><strong>Data de geração:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>

        <h3>Consultas Realizadas</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead style="background-color: #00b4d8; color: white;">
                <tr>
                    <th>ID</th>
                    <th>Paciente</th>
                    <th>Dentista</th>
                    <th>Data/Hora</th>
                    <th>Status</th>
                    <th>Data Cadastro</th>
                </tr>
            </thead>
            <tbody>
    '''

    for c in consultas:
        data_hora = c[3].split()[0] + ' ' + c[3].split()[1][:5] if c[3] else '-'
        data_cadastro = c[5].split()[0] if c[5] else '-'
        status = c[4]
        status_cor = '#28a745' if status == 'realizada' else '#ffc107' if status == 'agendada' else '#dc3545'
        html += f'''
        <tr>
            <td>{c[0]}</td>
            <td>{c[1]}</td>
            <td>{c[2] or '-'}</td>
            <td>{data_hora}</td>
            <td style="color: {status_cor}; font-weight: bold;">{status}</td>
            <td>{data_cadastro}</td>
        </tr>
        '''

    html += f'''
            </tbody>
        </table>

        <h3>Pacientes Cadastrados</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead style="background-color: #00b4d8; color: white;">
                <tr>
                    <th>Nome</th>
                    <th>Telefone</th>
                    <th>Email</th>
                    <th>Data Cadastro</th>
                </tr>
            </thead>
            <tbody>
    '''

    for p in pacientes:
        html += f'''
        <tr>
            <td>{p[0]}</td>
            <td>{p[1]}</td>
            <td>{p[2] or '-'}</td>
            <td>{p[3].split()[0] if p[3] else '-'}</td>
        </tr>
        '''

    html += '''
            </tbody>
        </table>

        <hr>
        <p style="color: #666; font-size: 12px;">Relatório gerado automaticamente pelo sistema</p>
    </body>
    </html>
    '''

    return StreamingResponse(
        io.BytesIO(html.encode('utf-8')),
        media_type='application/vnd.ms-excel',
        headers={
            'Content-Disposition': f'attachment; filename="relatorio_{inicio.strftime("%Y%m%d")}_{fim.strftime("%Y%m%d")}.xls"'
        }
    )

@relatorios_router.get('/relatorios/imprimir', name='relatorios_imprimir')
def relatorios_imprimir(request: Request):
    login_required(request)
    periodo = request.query_params.get('periodo', 30)
    data_inicio = request.query_params.get('data_inicio')
    data_fim = request.query_params.get('data_fim')

    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
    else:
        fim = datetime.now()
        inicio = fim - timedelta(days=int(periodo))

    db.cursor.execute('''
        SELECT
            c.id,
            c.nome_paciente,
            d.nome as dentista_nome,
            c.data_hora,
            c.status,
            c.created_at
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE date(c.created_at) BETWEEN date(?) AND date(?)
        ORDER BY c.created_at DESC
    ''', (inicio, fim))
    consultas = db.cursor.fetchall()

    db.cursor.execute('''
        SELECT nome, telefone, email, data_cadastro
        FROM pacientes
        WHERE date(data_cadastro) BETWEEN date(?) AND date(?)
        ORDER BY data_cadastro DESC
    ''', (inicio, fim))
    pacientes = db.cursor.fetchall()

    total_consultas = len(consultas)
    total_pacientes = len(pacientes)
    consultas_realizadas = sum(1 for c in consultas if c[4] == 'realizada')
    consultas_agendadas = sum(1 for c in consultas if c[4] == 'agendada')
    consultas_canceladas = sum(1 for c in consultas if c[4] == 'cancelada')

    return render(request, 'relatorios_imprimir.html',
                  inicio=inicio, fim=fim,
                  consultas=consultas, pacientes=pacientes,
                  total_consultas=total_consultas,
                  total_pacientes=total_pacientes,
                  consultas_realizadas=consultas_realizadas,
                  consultas_agendadas=consultas_agendadas,
                  consultas_canceladas=consultas_canceladas)

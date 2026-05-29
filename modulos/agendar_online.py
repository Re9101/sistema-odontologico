from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse, StreamingResponse
from datetime import date, datetime
import io
import qrcode

from extensions import db, login_required, render

agendar_online_router = APIRouter()

@agendar_online_router.get('/agendar-online', name='agendar_online')
def agendar_online(request: Request):
    db.cursor.execute('SELECT id, nome, especialidade FROM dentistas WHERE ativo = 1')
    dentistas = db.cursor.fetchall()

    db.cursor.execute('SELECT id, nome, valor FROM procedimentos WHERE ativo = 1')
    procedimentos = db.cursor.fetchall()

    return render(request, 'agendar_online.html', dentistas=dentistas, procedimentos=procedimentos, data_atual=date.today().isoformat())

@agendar_online_router.post('/agendar-online/buscar-horarios', name='buscar_horarios')
async def buscar_horarios(request: Request):
    form = await request.form()
    dentista_id = form.get('dentista_id')
    data = form.get('data')

    print(f"Buscando horários - Dentista: {dentista_id}, Data: {data}")

    if not dentista_id or not data:
        return {'erro': 'Dados incompletos'}

    try:
        datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        return {'erro': 'Data inválida'}

    db.cursor.execute('''
        SELECT data_hora FROM consultas
        WHERE dentista_id = ? AND DATE(data_hora) = ? AND status IN ('agendada', 'confirmada')
    ''', (dentista_id, data))

    ocupados = []
    for row in db.cursor.fetchall():
        data_hora_str = row[0]
        if ' ' in data_hora_str:
            hora_str = data_hora_str.split()[1]
            ocupados.append(hora_str[:5])

    print(f"Horários ocupados: {ocupados}")

    horarios = []
    for hora in range(8, 20):
        h = f"{hora:02d}:00"
        if h not in ocupados:
            horarios.append(h)

    print(f"Horários disponíveis: {horarios}")

    return {'horarios': horarios}

@agendar_online_router.post('/agendar-online/salvar', name='salvar_agendamento_online')
async def salvar_agendamento_online(request: Request):
    form = await request.form()
    print("=" * 50)
    print("Dados recebidos no agendamento:")
    for key, value in form.items():
        print(f"   {key}: {value}")
    print("=" * 50)

    nome = form.get('nome', '').strip()
    telefone = form.get('telefone', '').strip()
    email = form.get('email', '').strip()
    dentista_id = form.get('dentista_id', '').strip()
    procedimento_id = form.get('procedimento_id', '').strip()
    data = form.get('data', '').strip()
    hora = form.get('hora', '').strip()
    observacao = form.get('observacao', '').strip()

    if not nome:
        return "Erro: Nome é obrigatório", 400
    if not dentista_id:
        return "Erro: Selecione um dentista", 400
    if not data:
        return "Erro: Selecione uma data", 400
    if not hora:
        return "Erro: Selecione um horário", 400

    data_hora = f"{data} {hora}:00"

    try:
        db.cursor.execute('SELECT id FROM pacientes WHERE nome = ?', (nome,))
        paciente = db.cursor.fetchone()
        paciente_id = paciente[0] if paciente else None

        db.cursor.execute('''
            INSERT INTO consultas (nome_paciente, paciente_id, dentista_id, data_hora, observacoes, status)
            VALUES (?, ?, ?, ?, ?, 'agendada')
        ''', (nome, paciente_id, dentista_id, data_hora, observacao))
        db.conn.commit()

        consulta_id = db.cursor.lastrowid
        print(f"Agendamento salvo! ID: {consulta_id}")

        return render(request, 'agendamento_confirmado.html',
                       nome=nome, data=data, hora=hora, consulta_id=consulta_id)
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao salvar: {str(e)}", 500

@agendar_online_router.get('/agendamento-online/compartilhar', name='compartilhar_link')
def compartilhar_link(request: Request):
    login_required(request)
    link = str(request.url_for('agendar_online'))
    return render(request, 'compartilhar_link.html', link=link)

@agendar_online_router.get('/qrcode/{path:path}', name='gerar_qrcode')
def gerar_qrcode(path: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(path)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return StreamingResponse(img_io, media_type='image/png')

import sqlite3
from datetime import datetime, timedelta
import requests

# Configuração do CallMeBot
CALLMEBOT_API = "https://api.callmebot.com/whatsapp.php"
API_KEY = "5357145"

def enviar_whatsapp(telefone, mensagem):
    """Envia mensagem via WhatsApp usando CallMeBot"""
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    
    if len(telefone_limpo) >= 10:
        if not telefone_limpo.startswith('55'):
            telefone_limpo = '55' + telefone_limpo
    
    params = {
        'phone': telefone_limpo,
        'text': mensagem,
        'apikey': API_KEY
    }
    
    try:
        response = requests.get(CALLMEBOT_API, params=params, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"   Erro: {e}")
        return False

def enviar_todos_lembretes():
    conn = sqlite3.connect('static/database/clinica.db')
    cursor = conn.cursor()
    
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n🔍 Verificando consultas para {amanha}...")
    
    # Buscar consultas de amanhã (sem telefone por enquanto)
    cursor.execute('''
        SELECT c.id, c.nome_paciente, c.data_hora, d.nome as dentista_nome
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE date(c.data_hora) = ? AND c.status = 'agendada'
    ''', (amanha,))
    
    consultas = cursor.fetchall()
    
    if len(consultas) == 0:
        print("✅ Nenhuma consulta encontrada para amanhã!")
        conn.close()
        return
    
    print(f"\n📋 Total de consultas amanhã: {len(consultas)}")
    print("⚠️ Para enviar lembretes, adicione o telefone na consulta\n")
    
    for c in consultas:
        print(f"   📝 ID: {c[0]} | {c[1]} - {c[2].split()[0]} às {c[2].split()[1][:5]} - Dentista: {c[3]}")
    
    conn.close()

def enviar_lembrete_especifico(consulta_id, telefone):
    """Envia lembrete para uma consulta específica"""
    conn = sqlite3.connect('static/database/clinica.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.nome_paciente, c.data_hora, d.nome as dentista_nome
        FROM consultas c
        LEFT JOIN dentistas d ON c.dentista_id = d.id
        WHERE c.id = ?
    ''', (consulta_id,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if not resultado:
        print(f"❌ Consulta ID {consulta_id} não encontrada")
        return False
    
    nome_paciente = resultado[0]
    data = resultado[1].split()[0]
    hora = resultado[1].split()[1][:5]
    dentista = resultado[2]
    
    mensagem = f"""🦷 Clinica Sorriso Saudavel

Olá {nome_paciente}!

Lembrete de consulta:
Data: {data}
Horario: {hora}
Dentista: {dentista}

Por favor, confirme sua presenca.

Atenciosamente,
Equipe Sorriso Saudavel"""
    
    print(f"\n📝 Enviando lembrete para {nome_paciente}...")
    enviado = enviar_whatsapp(telefone, mensagem)
    
    if enviado:
        print(f"✅ Lembrete enviado com sucesso!")
    else:
        print(f"❌ Falha ao enviar")
    
    return enviado

if __name__ == '__main__':
    import sys
    
    print("🚀 SISTEMA DE LEMBRETES")
    print("=" * 40)
    
    if len(sys.argv) > 2 and sys.argv[1] == '--enviar':
        consulta_id = int(sys.argv[2])
        telefone = sys.argv[3] if len(sys.argv) > 3 else input("Digite o telefone: ")
        enviar_lembrete_especifico(consulta_id, telefone)
    else:
        enviar_todos_lembretes()
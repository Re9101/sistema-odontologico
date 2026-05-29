import sqlite3
from datetime import datetime, timedelta
import requests

# SUA API KEY DO CALLMEBOT
API_KEY = "5357145"

def enviar_whatsapp(telefone, mensagem):
    """Envia mensagem via WhatsApp usando CallMeBot"""
    # Remover caracteres especiais
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    
    # Garantir formato correto
    if len(telefone_limpo) == 11:
        telefone_limpo = telefone_limpo
    elif len(telefone_limpo) == 10:
        telefone_limpo = '55' + telefone_limpo
    elif len(telefone_limpo) == 13:
        telefone_limpo = telefone_limpo
    else:
        print(f"   Formato inválido: {telefone}")
        return False
    
    url = "https://api.callmebot.com/whatsapp.php"
    
    params = {
        'phone': telefone_limpo,
        'text': mensagem,
        'apikey': API_KEY
    }
    
    print(f"   Telefone: {telefone_limpo}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if "OK" in response.text or "Message" in response.text:
                return True
            else:
                print(f"   Resposta: {response.text}")
                return False
        else:
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"   Erro: {e}")
        return False

def enviar_lembrete_consulta(consulta_id, telefone):
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
    data_hora = resultado[1].split()
    data = data_hora[0]
    hora = data_hora[1][:5]
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
    return enviar_whatsapp(telefone, mensagem)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python lembretes.py CONSULTA_ID TELEFONE")
        print("Exemplo: python lembretes.py 6 5592984850163")
        sys.exit(1)
    
    consulta_id = int(sys.argv[1])
    telefone = sys.argv[2]
    
    resultado = enviar_lembrete_consulta(consulta_id, telefone)
    
    if resultado:
        print("\n✅ Lembrete enviado com sucesso!")
    else:
        print("\n❌ Falha ao enviar lembrete")
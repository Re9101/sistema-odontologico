import os
import hashlib
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

class Database:
    def __init__(self):
        # Pega a URL do banco do ambiente (Render fornece)
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            # Fallback para desenvolvimento local com SQLite
            import sqlite3
            db_path = 'static/database'
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            db_file = os.path.join(db_path, 'clinica.db')
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.is_sqlite = True
        else:
            # PostgreSQL no Render
            self.conn = psycopg2.connect(database_url)
            self.cursor = self.conn.cursor()
            self.is_sqlite = False
        
        self.criar_tabelas()
        self.inserir_dados_iniciais()

    def criar_tabelas(self):
        if self.is_sqlite:
            # Código SQLite original
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('admin', 'dentista', 'recepcionista')) NOT NULL,
                    nome_completo TEXT NOT NULL,
                    email TEXT,
                    celular TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # ... (restante do seu código SQLite original)
        else:
            # Código PostgreSQL
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('admin', 'dentista', 'recepcionista')) NOT NULL,
                    nome_completo TEXT NOT NULL,
                    email TEXT,
                    celular TEXT,
                    ativo BOOLEAN DEFAULT TRUE,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    email TEXT,
                    data_nascimento TEXT,
                    convenio TEXT,
                    responsavel TEXT,
                    alergias TEXT,
                    observacoes TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dentistas (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    cro TEXT UNIQUE NOT NULL,
                    especialidade TEXT,
                    telefone TEXT,
                    email TEXT,
                    horario_inicio TEXT DEFAULT '08:00',
                    horario_fim TEXT DEFAULT '18:00',
                    ativo BOOLEAN DEFAULT TRUE,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS procedimentos (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    duracao_minutos INTEGER DEFAULT 60,
                    valor DECIMAL(10,2),
                    codigo_tuss TEXT,
                    ativo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS consultas (
                    id SERIAL PRIMARY KEY,
                    nome_paciente TEXT NOT NULL,
                    dentista_id INTEGER NOT NULL,
                    procedimento_id INTEGER,
                    paciente_id INTEGER,
                    data_hora TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'agendada',
                    dente_regiao TEXT,
                    observacoes TEXT,
                    queixa_principal TEXT,
                    diagnostico TEXT,
                    tratamento_realizado TEXT,
                    medicamentos_receitados TEXT,
                    retorno_data TEXT,
                    valor_pago DECIMAL(10,2),
                    forma_pagamento TEXT,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE SET NULL,
                    FOREIGN KEY (dentista_id) REFERENCES dentistas(id) ON DELETE CASCADE,
                    FOREIGN KEY (procedimento_id) REFERENCES procedimentos(id) ON DELETE SET NULL
                )
            ''')
        
        self.conn.commit()

    def inserir_dados_iniciais(self):
        # Verificar se usuário admin existe
        self.cursor.execute('SELECT COUNT(*) FROM usuarios')
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO usuarios (username, senha, tipo, nome_completo, email, celular, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', ('admin', senha_hash, 'admin', 'Administrador do Sistema', 'admin@clinica.com', '(11) 99999-1234', True))
            print("Usuario admin criado (usuario: admin / senha: admin123)")
        
        # Verificar se procedimentos existem
        self.cursor.execute('SELECT COUNT(*) FROM procedimentos')
        count_proc = self.cursor.fetchone()[0]
        
        if count_proc == 0:
            procedimentos_padrao = [
                ('Avaliação Inicial', 'Primeira consulta, avaliação completa', 30, 150.00, 'AV001'),
                ('Limpeza (Profilaxia)', 'Limpeza e remoção de tártaro', 40, 200.00, 'LP002'),
                ('Restauração', 'Tratamento de cárie', 60, 250.00, 'RT003'),
                ('Canal (Endodontia)', 'Tratamento de canal', 90, 500.00, 'CN004'),
                ('Extração Simples', 'Remoção de dente', 45, 180.00, 'EX005'),
                ('Extração Cirúrgica', 'Remoção de dente incluso', 60, 350.00, 'EC006'),
                ('Clareamento', 'Clareamento dental a laser', 60, 800.00, 'CL007'),
                ('Aparelho Ortodôntico', 'Colocação de aparelho', 90, 1200.00, 'AP008'),
                ('Manutenção', 'Ajuste de aparelho', 30, 100.00, 'MN009'),
                ('Raio-X', 'Exame radiográfico', 15, 80.00, 'RX010'),
            ]
            
            if self.is_sqlite:
                self.cursor.executemany('''
                    INSERT INTO procedimentos (nome, descricao, duracao_minutos, valor, codigo_tuss)
                    VALUES (?, ?, ?, ?, ?)
                ''', procedimentos_padrao)
            else:
                self.cursor.executemany('''
                    INSERT INTO procedimentos (nome, descricao, duracao_minutos, valor, codigo_tuss)
                    VALUES (%s, %s, %s, %s, %s)
                ''', procedimentos_padrao)
            
            print("Procedimentos padrao criados!")
        
        self.conn.commit()

    def close(self):
        self.conn.close()

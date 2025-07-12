import sqlite3
import os

def criar_banco_de_dados():
    """
    Cria todas as 12 tabelas necessárias para o sistema se elas não existirem.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'database.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("[DB SETUP] Verificando e criando tabelas...")

    # 1. Tabela Operadores
    c.execute('''
        CREATE TABLE IF NOT EXISTS Operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            papel TEXT NOT NULL CHECK(papel IN ('Administrador', 'Porteiro', 'COAPAC')),
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Tabela Cursos
    c.execute('''
        CREATE TABLE IF NOT EXISTS Cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_curso TEXT NOT NULL UNIQUE
        )
    ''')

    # 3. Tabela Turmas
    c.execute('''
        CREATE TABLE IF NOT EXISTS Turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_turma TEXT NOT NULL,
            curso_id INTEGER,
            ano INTEGER,
            turno TEXT,
            FOREIGN KEY (curso_id) REFERENCES Cursos(id)
        )
    ''')

    # 4. Tabela Usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            matricula TEXT UNIQUE,
            tipo TEXT CHECK(tipo IN ('Discente', 'Docente', 'Servidor')),
            situacao TEXT DEFAULT 'Normal' CHECK(situacao IN ('Normal', 'Advertido', 'Suspenso')),
            caminho_foto_rosto TEXT NOT NULL
        )
    ''')

    # 5. Tabela UsuarioTurma (Associação)
    c.execute('''
        CREATE TABLE IF NOT EXISTS UsuarioTurma (
            usuario_id INTEGER NOT NULL,
            turma_id INTEGER NOT NULL,
            PRIMARY KEY (usuario_id, turma_id),
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (turma_id) REFERENCES Turmas(id) ON DELETE CASCADE
        )
    ''')

    # 6. Tabela Visitantes
    c.execute('''
        CREATE TABLE IF NOT EXISTS Visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            documento TEXT NOT NULL,
            empresa TEXT,
            motivo_acesso TEXT,
            horario_programado_inicio DATETIME,
            horario_programado_fim DATETIME,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. Tabela LogsAcesso
    c.execute('''
        CREATE TABLE IF NOT EXISTS LogsAcesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_acesso TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Aceito', 'Negado', 'Não Encontrado')),
            usuario_id INTEGER,
            visitante_id INTEGER,
            caminho_foto_capturada TEXT,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
            FOREIGN KEY (visitante_id) REFERENCES Visitantes(id)
        )
    ''')

    # 8. Tabela AcoesDisciplinares
    c.execute('''
        CREATE TABLE IF NOT EXISTS AcoesDisciplinares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            operador_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('Advertência', 'Suspensão')),
            motivo TEXT,
            data_inicio DATE,
            data_fim DATE,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
            FOREIGN KEY (operador_id) REFERENCES Operadores(id)
        )
    ''')

    # 9. Tabela PermissoesEspeciais
    c.execute('''
        CREATE TABLE IF NOT EXISTS PermissoesEspeciais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            operador_id INTEGER NOT NULL,
            justificativa TEXT,
            data_hora_permissao DATETIME,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
            FOREIGN KEY (operador_id) REFERENCES Operadores(id)
        )
    ''')

    # 10. Tabela LiberacoesCOAPAC
    c.execute('''
        CREATE TABLE IF NOT EXISTS LiberacoesCOAPAC (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER NOT NULL,
            operador_id INTEGER NOT NULL,
            justificativa TEXT,
            data_liberacao DATE,
            horario_liberacao TIME,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (turma_id) REFERENCES Turmas(id),
            FOREIGN KEY (operador_id) REFERENCES Operadores(id)
        )
    ''')

    # 11. Tabela Anuncios
    c.execute('''
        CREATE TABLE IF NOT EXISTS Anuncios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('Evento', 'Lembrete')),
            titulo TEXT,
            legenda TEXT,
            caminho_imagem TEXT,
            data_inicio_exibicao DATE,
            data_fim_exibicao DATE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operador_id) REFERENCES Operadores(id)
        )
    ''')

    # 12. Tabela Notificacoes
    c.execute('''
        CREATE TABLE IF NOT EXISTS Notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador_id INTEGER NOT NULL,
            mensagem TEXT,
            tipo_alerta TEXT,
            link_relacionado TEXT,
            lida BOOLEAN DEFAULT FALSE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operador_id) REFERENCES Operadores(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB SETUP] Configuração do banco de dados concluída.")


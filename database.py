"""
Módulo de acesso ao banco de dados (SQLite) para o Clínica Vida.
Responsável por criar a tabela e fazer CRUD de pacientes.
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "clinica_vida.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Cria as tabelas se elas ainda não existirem."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                data_nascimento TEXT,
                cpf TEXT UNIQUE,
                rg TEXT,
                sexo TEXT,
                estado_civil TEXT,
                cep TEXT,
                logradouro TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                criado_em TEXT DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                tipo TEXT,
                medico TEXT,
                status TEXT DEFAULT 'Agendada',
                observacoes TEXT,
                criado_em TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
            """
        )


def inserir_paciente(dados: dict):
    """Insere um novo paciente. Retorna (sucesso: bool, mensagem: str)."""
    campos = [
        "nome_completo", "data_nascimento", "cpf", "rg", "sexo",
        "estado_civil", "cep", "logradouro", "numero", "complemento",
        "bairro", "cidade", "estado",
    ]
    valores = [dados.get(c, "") for c in campos]
    placeholders = ", ".join("?" for _ in campos)
    colunas = ", ".join(campos)

    try:
        with get_connection() as conn:
            conn.execute(
                f"INSERT INTO pacientes ({colunas}) VALUES ({placeholders})",
                valores,
            )
        return True, "Paciente cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Já existe um paciente cadastrado com esse CPF."
    except Exception as e:
        return False, f"Erro ao cadastrar paciente: {e}"


def atualizar_paciente(paciente_id: int, dados: dict):
    campos = [
        "nome_completo", "data_nascimento", "cpf", "rg", "sexo",
        "estado_civil", "cep", "logradouro", "numero", "complemento",
        "bairro", "cidade", "estado",
    ]
    set_clause = ", ".join(f"{c} = ?" for c in campos)
    valores = [dados.get(c, "") for c in campos] + [paciente_id]

    try:
        with get_connection() as conn:
            conn.execute(
                f"UPDATE pacientes SET {set_clause} WHERE id = ?", valores
            )
        return True, "Paciente atualizado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Já existe um paciente cadastrado com esse CPF."
    except Exception as e:
        return False, f"Erro ao atualizar paciente: {e}"


def listar_pacientes(termo_busca: str = ""):
    """Retorna lista de pacientes, opcionalmente filtrada por nome ou CPF."""
    with get_connection() as conn:
        if termo_busca:
            cursor = conn.execute(
                """
                SELECT * FROM pacientes
                WHERE nome_completo LIKE ? OR cpf LIKE ?
                ORDER BY nome_completo
                """,
                (f"%{termo_busca}%", f"%{termo_busca}%"),
            )
        else:
            cursor = conn.execute("SELECT * FROM pacientes ORDER BY nome_completo")
        return [dict(row) for row in cursor.fetchall()]


def obter_paciente(paciente_id: int):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def excluir_paciente(paciente_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))


def contar_pacientes():
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) as total FROM pacientes")
        return cursor.fetchone()["total"]


# --------------------------------------------------------------
# Consultas (Agenda)
# --------------------------------------------------------------

def inserir_consulta(dados: dict):
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO consultas (paciente_id, data, hora, tipo, medico, status, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados["paciente_id"], dados["data"], dados["hora"],
                    dados.get("tipo", ""), dados.get("medico", ""),
                    dados.get("status", "Agendada"), dados.get("observacoes", ""),
                ),
            )
        return True, "Consulta agendada com sucesso!"
    except Exception as e:
        return False, f"Erro ao agendar consulta: {e}"


def listar_consultas(data_filtro: str = None):
    with get_connection() as conn:
        if data_filtro:
            cursor = conn.execute(
                """
                SELECT consultas.*, pacientes.nome_completo
                FROM consultas
                JOIN pacientes ON pacientes.id = consultas.paciente_id
                WHERE consultas.data = ?
                ORDER BY consultas.hora
                """,
                (data_filtro,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT consultas.*, pacientes.nome_completo
                FROM consultas
                JOIN pacientes ON pacientes.id = consultas.paciente_id
                ORDER BY consultas.data, consultas.hora
                """
            )
        return [dict(row) for row in cursor.fetchall()]


def atualizar_status_consulta(consulta_id: int, novo_status: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE consultas SET status = ? WHERE id = ?", (novo_status, consulta_id)
        )


def excluir_consulta(consulta_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))


def contar_consultas_hoje(hoje: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) as total FROM consultas WHERE data = ?", (hoje,)
        )
        return cursor.fetchone()["total"]


# --------------------------------------------------------------
# Configurações (chave/valor)
# --------------------------------------------------------------

def salvar_configuracao(chave: str, valor: str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO configuracoes (chave, valor) VALUES (?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
            """,
            (chave, valor),
        )


def salvar_configuracoes(dados: dict):
    """Salva várias configurações de uma vez (mesma transação)."""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO configuracoes (chave, valor) VALUES (?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
            """,
            list(dados.items()),
        )


def obter_configuracao(chave: str, padrao=None):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT valor FROM configuracoes WHERE chave = ?", (chave,)
        )
        row = cursor.fetchone()
        return row["valor"] if row else padrao


def obter_todas_configuracoes():
    with get_connection() as conn:
        cursor = conn.execute("SELECT chave, valor FROM configuracoes")
        return {row["chave"]: row["valor"] for row in cursor.fetchall()}

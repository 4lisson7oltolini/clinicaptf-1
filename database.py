import sqlite3
from contextlib import contextmanager

DB_PATH = "clinica_cdm"

@contextmanager
def get_conection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """Criar a tabela de pacientes."""
    with get_conection() as conn:
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
        with get_conection() as conn:
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
        with get_conection() as conn:
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
    with get_conection() as conn:
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
    with get_conection() as conn:
        cursor = conn.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
 
 
def excluir_paciente(paciente_id: int):
    with get_conection() as conn:
        conn.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
 
 
def contar_pacientes():
    with get_conection() as conn:
        cursor = conn.execute("SELECT COUNT(*) as total FROM pacientes")
        return cursor.fetchone()["total"]

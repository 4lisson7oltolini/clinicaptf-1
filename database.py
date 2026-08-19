import sqlite3
from contextlib import contextmanager

# ------------------------------------------------------------------
# Configuração do banco
# ------------------------------------------------------------------

DB_PATH = "clinica_vida.db"


# ------------------------------------------------------------------
# Conexão com o banco
# ------------------------------------------------------------------

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ------------------------------------------------------------------
# Inicialização do banco
# ------------------------------------------------------------------

def init_db():
    """Cria as tabelas necessárias para o sistema."""

    with get_connection() as conn:

        # ----------------------------------------------------------
        # Tabela de pacientes
        # ----------------------------------------------------------

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

        # ----------------------------------------------------------
        # Tabela de consultas
        # ----------------------------------------------------------

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                paciente_id INTEGER NOT NULL,

                data TEXT NOT NULL,
                hora TEXT NOT NULL,

                tipo TEXT,
                medico TEXT,
                observacoes TEXT,

                status TEXT DEFAULT 'Agendada',

                criado_em TEXT DEFAULT (datetime('now', 'localtime')),

                FOREIGN KEY (paciente_id)
                    REFERENCES pacientes(id)
                    ON DELETE CASCADE
            )
            """
        )


# ------------------------------------------------------------------
# PACIENTES
# ------------------------------------------------------------------

def inserir_paciente(dados: dict):
    """Insere um novo paciente."""

    campos = [
        "nome_completo",
        "data_nascimento",
        "cpf",
        "rg",
        "sexo",
        "estado_civil",
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    ]

    valores = [dados.get(c, "") for c in campos]

    placeholders = ", ".join("?" for _ in campos)
    colunas = ", ".join(campos)

    try:
        with get_connection() as conn:
            conn.execute(
                f"""
                INSERT INTO pacientes ({colunas})
                VALUES ({placeholders})
                """,
                valores,
            )

        return True, "Paciente cadastrado com sucesso!"

    except sqlite3.IntegrityError:
        return False, "Já existe um paciente cadastrado com esse CPF."

    except Exception as e:
        return False, f"Erro ao cadastrar paciente: {e}"


def atualizar_paciente(paciente_id: int, dados: dict):
    """Atualiza os dados de um paciente."""

    campos = [
        "nome_completo",
        "data_nascimento",
        "cpf",
        "rg",
        "sexo",
        "estado_civil",
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    ]

    set_clause = ", ".join(f"{campo} = ?" for campo in campos)

    valores = [
        dados.get(campo, "")
        for campo in campos
    ]

    valores.append(paciente_id)

    try:
        with get_connection() as conn:
            conn.execute(
                f"""
                UPDATE pacientes
                SET {set_clause}
                WHERE id = ?
                """,
                valores,
            )

        return True, "Paciente atualizado com sucesso!"

    except sqlite3.IntegrityError:
        return False, "Já existe um paciente cadastrado com esse CPF."

    except Exception as e:
        return False, f"Erro ao atualizar paciente: {e}"


def listar_pacientes(termo_busca: str = ""):
    """Lista todos os pacientes ou filtra por nome/CPF."""

    with get_connection() as conn:

        if termo_busca:

            cursor = conn.execute(
                """
                SELECT *
                FROM pacientes
                WHERE nome_completo LIKE ?
                   OR cpf LIKE ?
                ORDER BY nome_completo
                """,
                (
                    f"%{termo_busca}%",
                    f"%{termo_busca}%",
                ),
            )

        else:

            cursor = conn.execute(
                """
                SELECT *
                FROM pacientes
                ORDER BY nome_completo
                """
            )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


def obter_paciente(paciente_id: int):
    """Obtém um paciente pelo ID."""

    with get_connection() as conn:

        cursor = conn.execute(
            """
            SELECT *
            FROM pacientes
            WHERE id = ?
            """,
            (paciente_id,),
        )

        row = cursor.fetchone()

        if row:
            return dict(row)

        return None


def excluir_paciente(paciente_id: int):
    """Exclui um paciente."""

    try:

        with get_connection() as conn:

            # Primeiro excluímos as consultas relacionadas
            conn.execute(
                """
                DELETE FROM consultas
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )

            # Depois excluímos o paciente
            conn.execute(
                """
                DELETE FROM pacientes
                WHERE id = ?
                """,
                (paciente_id,),
            )

        return True

    except Exception:
        return False


def contar_pacientes():
    """Retorna o número total de pacientes."""

    with get_connection() as conn:

        cursor = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM pacientes
            """
        )

        return cursor.fetchone()["total"]


# ------------------------------------------------------------------
# CONSULTAS
# ------------------------------------------------------------------

def inserir_consulta(dados: dict):
    """Agenda uma nova consulta."""

    try:

        with get_connection() as conn:

            # Verifica se o paciente existe
            paciente = conn.execute(
                """
                SELECT id
                FROM pacientes
                WHERE id = ?
                """,
                (dados.get("paciente_id"),),
            ).fetchone()

            if not paciente:
                return False, "Paciente não encontrado."

            conn.execute(
                """
                INSERT INTO consultas (
                    paciente_id,
                    data,
                    hora,
                    tipo,
                    medico,
                    observacoes,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados.get("paciente_id"),
                    dados.get("data", ""),
                    dados.get("hora", ""),
                    dados.get("tipo", ""),
                    dados.get("medico", ""),
                    dados.get("observacoes", ""),
                    "Agendada",
                ),
            )

        return True, "Consulta agendada com sucesso!"

    except Exception as e:

        return False, f"Erro ao agendar consulta: {e}"


def listar_consultas(data_filtro=None):
    """
    Lista consultas.

    Se data_filtro for informada, retorna somente
    as consultas daquela data.
    """

    with get_connection() as conn:

        if data_filtro:

            cursor = conn.execute(
                """
                SELECT
                    consultas.*,
                    pacientes.nome_completo,
                    pacientes.cpf

                FROM consultas

                INNER JOIN pacientes
                    ON consultas.paciente_id = pacientes.id

                WHERE consultas.data = ?

                ORDER BY
                    consultas.data,
                    consultas.hora
                """,
                (data_filtro,),
            )

        else:

            cursor = conn.execute(
                """
                SELECT
                    consultas.*,
                    pacientes.nome_completo,
                    pacientes.cpf

                FROM consultas

                INNER JOIN pacientes
                    ON consultas.paciente_id = pacientes.id

                ORDER BY
                    consultas.data,
                    consultas.hora
                """
            )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


def atualizar_status_consulta(
    consulta_id: int,
    novo_status: str
):
    """Atualiza o status de uma consulta."""

    status_validos = [
        "Agendada",
        "Confirmada",
        "Concluída",
        "Cancelada",
    ]

    if novo_status not in status_validos:
        return False

    try:

        with get_connection() as conn:

            cursor = conn.execute(
                """
                UPDATE consultas

                SET status = ?

                WHERE id = ?
                """,
                (
                    novo_status,
                    consulta_id,
                ),
            )

            return cursor.rowcount > 0

    except Exception:
        return False


def excluir_consulta(consulta_id: int):
    """Exclui uma consulta."""

    try:

        with get_connection() as conn:

            cursor = conn.execute(
                """
                DELETE FROM consultas
                WHERE id = ?
                """,
                (consulta_id,),
            )

            return cursor.rowcount > 0

    except Exception:
        return False


def contar_consultas_hoje(data=None):
    """
    Retorna a quantidade de consultas de uma determinada data.

    Se nenhuma data for informada, utiliza a data atual.
    """

    if data is None:

        from datetime import date

        data = date.today().isoformat()

    with get_connection() as conn:

        cursor = conn.execute(
            """
            SELECT COUNT(*) AS total

            FROM consultas

            WHERE data = ?
            """,
            (data,),
        )

        return cursor.fetchone()["total"]
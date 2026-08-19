import streamlit as st
import pandas as pd
from datetime import date

from database import (
    init_db, inserir_paciente, atualizar_paciente, listar_pacientes,
    obter_paciente, excluir_paciente, contar_pacientes,
)
from utils import validar_cpf, formatar_cpf, formatar_cep, ESTADOS_BR

# ------------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Clínica Vida - Sistema de Gestão",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ------------------------------------------------------------------
# Estado de sessão
# ------------------------------------------------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"
if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

# ------------------------------------------------------------------
# CSS customizado (paleta azul/teal inspirada no design de referência)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --azul-principal: #1596ac;
        --azul-escuro: #0d7c90;
        --azul-claro: #e3f6f9;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1596ac 0%, #0d7c90 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent;
        border: none;
        text-align: left;
        width: 100%;
        border-radius: 8px;
        padding: 0.55rem 0.9rem;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }
    section[data-testid="stSidebar"] .stButton button:focus {
        box-shadow: none !important;
    }

    /* Cards / containers */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #eaeaea;
    }

    .cv-metric {
        background-color: #ffffff;
        border: 1px solid #eaeaea;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
    }

    h1, h2, h3 {
        color: #1a2b3c;
    }

    .cv-subtitulo {
        color: #6b7c93;
        margin-top: -10px;
    }

    .stButton > button[kind="primary"] {
        background-color: var(--azul-principal);
        border-color: var(--azul-principal);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; padding: 0.5rem 0 1.2rem 0;">
            <div style="background:rgba(255,255,255,0.15); border-radius:8px; width:38px; height:38px;
                        display:flex; align-items:center; justify-content:center; font-size:20px;">🏥</div>
            <div>
                <div style="font-weight:700; font-size:1.05rem; line-height:1.1;">Clínica Vida</div>
                <div style="font-size:0.75rem; opacity:0.85;">Sistema de Gestão</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = [
        ("🏠", "Início"),
        ("👥", "Pacientes"),
        ("📅", "Agenda"),
        ("📄", "Relatórios"),
        ("⚙️", "Configurações"),
    ]
    for icone, nome in menu:
        if st.button(f"{icone}  {nome}", key=f"nav_{nome}", use_container_width=True):
            st.session_state.pagina = nome
            st.session_state.editando_id = None

    st.markdown("<div style='flex-grow:1;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("❓  Ajuda", use_container_width=True)


# ------------------------------------------------------------------
# Página: Início
# ------------------------------------------------------------------
def pagina_inicio():
    st.title("Início")
    st.markdown("<p class='cv-subtitulo'>Visão geral do sistema</p>", unsafe_allow_html=True)
    st.write("")

    total = contar_pacientes()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='cv-metric'><div style='color:#6b7c93; font-size:0.85rem;'>Total de Pacientes</div>"
            f"<div style='font-size:1.8rem; font-weight:700; color:#1596ac;'>{total}</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div class='cv-metric'><div style='color:#6b7c93; font-size:0.85rem;'>Consultas Hoje</div>"
            "<div style='font-size:1.8rem; font-weight:700; color:#1596ac;'>0</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            "<div class='cv-metric'><div style='color:#6b7c93; font-size:0.85rem;'>Relatórios Pendentes</div>"
            "<div style='font-size:1.8rem; font-weight:700; color:#1596ac;'>0</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader("Últimos pacientes cadastrados")
    pacientes = listar_pacientes()
    if pacientes:
        df = pd.DataFrame(pacientes).sort_values("id", ascending=False).head(5)
        st.dataframe(
            df[["nome_completo", "cpf", "cidade", "criado_em"]].rename(
                columns={
                    "nome_completo": "Nome",
                    "cpf": "CPF",
                    "cidade": "Cidade",
                    "criado_em": "Cadastrado em",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum paciente cadastrado ainda. Vá em **Pacientes** para começar.")


# ------------------------------------------------------------------
# Página: Pacientes (lista + formulário)
# ------------------------------------------------------------------
def formulario_paciente():
    editando = st.session_state.editando_id is not None
    dados_atuais = obter_paciente(st.session_state.editando_id) if editando else {}

    titulo = "Editar Paciente" if editando else "Cadastro de Paciente"
    st.subheader(titulo)
    st.markdown("<p class='cv-subtitulo'>Preencha os dados do paciente</p>", unsafe_allow_html=True)
    st.write("")

    with st.form("form_paciente", clear_on_submit=not editando):
        st.markdown("**👤 Informações do Paciente**")
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome Completo*", value=dados_atuais.get("nome_completo", ""))
        try:
            data_nasc_default = (
                date.fromisoformat(dados_atuais["data_nascimento"])
                if dados_atuais.get("data_nascimento")
                else None
            )
        except ValueError:
            data_nasc_default = None
        data_nasc = c2.date_input(
            "Data de Nascimento",
            value=data_nasc_default,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )
        cpf = c3.text_input("CPF*", value=dados_atuais.get("cpf", ""), placeholder="000.000.000-00")

        c4, c5 = st.columns(2)
        sexo_opcoes = ["Selecione", "Feminino", "Masculino", "Outro"]
        sexo_idx = sexo_opcoes.index(dados_atuais["sexo"]) if dados_atuais.get("sexo") in sexo_opcoes else 0
        sexo = c4.selectbox("Sexo", sexo_opcoes, index=sexo_idx)

        civil_opcoes = ["Selecione", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"]
        civil_idx = (
            civil_opcoes.index(dados_atuais["estado_civil"])
            if dados_atuais.get("estado_civil") in civil_opcoes
            else 0
        )
        estado_civil = c5.selectbox("Estado Civil", civil_opcoes, index=civil_idx)

        st.markdown("**📍 Endereço**")
        c7, c8 = st.columns([1, 2])
        cep = c7.text_input("CEP", value=dados_atuais.get("cep", ""), placeholder="00000-000")
        logradouro = c8.text_input(
            "Logradouro", value=dados_atuais.get("logradouro", ""), placeholder="Rua, Avenida, etc."
        )

        c9, c10, c11 = st.columns(3)
        numero = c9.text_input("Número", value=dados_atuais.get("numero", ""), placeholder="Nº")
        complemento = c10.text_input(
            "Complemento", value=dados_atuais.get("complemento", ""), placeholder="Apto, Sala, etc."
        )
        bairro = c11.text_input("Bairro", value=dados_atuais.get("bairro", ""))

        c12, c13 = st.columns(2)
        cidade = c12.text_input("Cidade", value=dados_atuais.get("cidade", ""))
        estado_opcoes = ["Selecione"] + ESTADOS_BR
        estado_idx = (
            estado_opcoes.index(dados_atuais["estado"]) if dados_atuais.get("estado") in estado_opcoes else 0
        )
        estado = c13.selectbox("Estado", estado_opcoes, index=estado_idx)

        st.write("")
        col_a, col_b = st.columns([1, 5])
        salvar = col_a.form_submit_button(
            "Salvar" if not editando else "Atualizar", type="primary", use_container_width=True
        )
        cancelar = col_b.form_submit_button("Cancelar", use_container_width=False) if editando else False

        if salvar:
            if not nome.strip():
                st.error("O campo **Nome Completo** é obrigatório.")
            elif not validar_cpf(cpf):
                st.error("CPF inválido. Verifique os números digitados.")
            else:
                dados = {
                    "nome_completo": nome.strip(),
                    "data_nascimento": data_nasc.isoformat() if data_nasc else "",
                    "cpf": formatar_cpf(cpf),
                    "sexo": sexo if sexo != "Selecione" else "",
                    "estado_civil": estado_civil if estado_civil != "Selecione" else "",
                    "cep": formatar_cep(cep),
                    "logradouro": logradouro.strip(),
                    "numero": numero.strip(),
                    "complemento": complemento.strip(),
                    "bairro": bairro.strip(),
                    "cidade": cidade.strip(),
                    "estado": estado if estado != "Selecione" else "",
                }
                if editando:
                    sucesso, msg = atualizar_paciente(st.session_state.editando_id, dados)
                else:
                    sucesso, msg = inserir_paciente(dados)

                if sucesso:
                    st.session_state.editando_id = None
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        if cancelar:
            st.session_state.editando_id = None
            st.rerun()


def lista_pacientes():
    st.write("")
    st.subheader("Pacientes Cadastrados")
    busca = st.text_input("🔍 Buscar por nome ou CPF", key="busca_paciente")
    pacientes = listar_pacientes(busca)

    if not pacientes:
        st.info("Nenhum paciente encontrado.")
        return

    for p in pacientes:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 3, 2])
            c1.markdown(f"**{p['nome_completo']}**  \n📞 CPF: {p['cpf'] or '—'}")
            c2.markdown(
                f"📍 {p['cidade'] or '—'}{'/' + p['estado'] if p['estado'] else ''}  \n"
                f"🎂 {p['data_nascimento'] or '—'}"
            )
            b1, b2 = c3.columns(2)
            if b1.button("✏️ Editar", key=f"editar_{p['id']}", use_container_width=True):
                st.session_state.editando_id = p["id"]
                st.rerun()
            if b2.button("🗑️ Excluir", key=f"excluir_{p['id']}", use_container_width=True):
                excluir_paciente(p["id"])
                st.success(f"Paciente {p['nome_completo']} removido.")
                st.rerun()


def pagina_pacientes():
    st.title("Pacientes")
    aba_cadastro, aba_lista = st.tabs(["📝 Cadastro", "📋 Lista de Pacientes"])
    with aba_cadastro:
        formulario_paciente()
    with aba_lista:
        lista_pacientes()


# ------------------------------------------------------------------
# Páginas placeholder (Agenda, Relatórios, Configurações)
# ------------------------------------------------------------------
def pagina_placeholder(nome, icone):
    st.title(nome)
    st.info(f"{icone} A seção **{nome}** ainda será implementada.")


# ------------------------------------------------------------------
# Roteamento
# ------------------------------------------------------------------
pagina = st.session_state.pagina
if pagina == "Início":
    pagina_inicio()
elif pagina == "Pacientes":
    pagina_pacientes()
elif pagina == "Agenda":
    pagina_placeholder("Agenda", "📅")
elif pagina == "Relatórios":
    pagina_placeholder("Relatórios", "📄")
elif pagina == "Configurações":
    pagina_placeholder("Configurações", "⚙️")
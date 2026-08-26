import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path
from datetime import date, datetime
from PIL import Image

from database import (
    init_db, inserir_paciente, atualizar_paciente, listar_pacientes,
    obter_paciente, excluir_paciente, contar_pacientes,
    inserir_consulta, listar_consultas, atualizar_status_consulta,
    excluir_consulta, contar_consultas_hoje,
    salvar_configuracoes, obter_todas_configuracoes,
)
from utils import validar_cpf, formatar_cpf, formatar_cep, validar_email, ESTADOS_BR

# ------------------------------------------------------------------
# Banco de dados e configurações salvas (carregados antes da UI
# para poder usar o nome da clínica no título/favicon da página)
# ------------------------------------------------------------------
init_db()

_DEFAULTS_CONFIG = {
    "nome_clinica": "Clínica PTF",
    "telefone_clinica": "",
    "email_clinica": "",
    "endereco_clinica": "",
    "filial_estado": "Selecione",
    "filial_cidade": "",
    "tamanho_fonte": "100",
    "alto_contraste": "False",
    "reduzir_animacoes": "False",
    "tema_tabela": "Confortável",
}

if "config" not in st.session_state:
    salvas = obter_todas_configuracoes()
    st.session_state.config = {**_DEFAULTS_CONFIG, **salvas}

cfg = st.session_state.config

# ------------------------------------------------------------------
# Logo da clínica (carregada antes do set_page_config para servir de favicon)
# ------------------------------------------------------------------
_LOGO_PATH = Path(__file__).parent / "assets" / "logo_small.png"
_pagina_icone = "🏥"
if _LOGO_PATH.exists():
    try:
        _pagina_icone = Image.open(_LOGO_PATH)
    except Exception:
        _pagina_icone = "🏥"

# ------------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------------
st.set_page_config(
    page_title=f"{cfg.get('nome_clinica', 'Clínica PTF')} - Sistema de Gestão",
    page_icon=_pagina_icone,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Logo em base64 (para uso inline no HTML da sidebar)
# ------------------------------------------------------------------
@st.cache_data
def carregar_logo_base64():
    if _LOGO_PATH.exists():
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode("utf-8")
    return None


logo_base64 = carregar_logo_base64()

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
        --azul-claro: #e6f7ec;
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
# CSS de acessibilidade (aplicado com base nas configurações salvas)
# ------------------------------------------------------------------
_tamanho_fonte = cfg.get("tamanho_fonte", "100")
_alto_contraste = cfg.get("alto_contraste", "False") == "True"
_reduzir_animacoes = cfg.get("reduzir_animacoes", "False") == "True"

_css_acessibilidade = f"""
<style>
html {{
    font-size: {_tamanho_fonte}% !important;
}}
"""

if _alto_contraste:
    _css_acessibilidade += """
section[data-testid="stSidebar"] {
    background: #000000 !important;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background-color: rgba(255, 255, 255, 0.35) !important;
}
body, .stApp, p, span, label, div {
    color: #000000;
}
h1, h2, h3, h4 {
    color: #000000 !important;
}
div[data-testid="stForm"], .cv-metric, div[data-testid="stContainer"] {
    border: 2px solid #000000 !important;
    background-color: #ffffff !important;
}
.stButton > button {
    border: 2px solid #000000 !important;
}
.stButton > button[kind="primary"] {
    background-color: #000000 !important;
    border-color: #000000 !important;
    color: #ffffff !important;
}
a, .cv-subtitulo {
    color: #000000 !important;
    text-decoration: underline !important;
}
input, textarea, select {
    border: 2px solid #000000 !important;
}
"""

if _reduzir_animacoes:
    _css_acessibilidade += """
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
    scroll-behavior: auto !important;
}
"""

_css_acessibilidade += "</style>"

st.markdown(_css_acessibilidade, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    if logo_base64:
        logo_html = (
            f'<img src="data:image/png;base64,{logo_base64}" '
            f'style="width:44px; height:44px; object-fit:contain;" />'
        )
    else:
        logo_html = (
            '<div style="background:rgba(255,255,255,0.15); border-radius:8px; width:38px; height:38px; '
            'display:flex; align-items:center; justify-content:center; font-size:20px;">🏥</div>'
        )

    _nome_exibido = cfg.get("nome_clinica", "Clínica PTF") or "Clínica PTF"
    _filial_estado = cfg.get("filial_estado", "Selecione")
    _filial_cidade = cfg.get("filial_cidade", "")
    if _filial_estado and _filial_estado != "Selecione":
        _subtitulo = f"{_filial_cidade + ' - ' if _filial_cidade else ''}{_filial_estado}"
    else:
        _subtitulo = "Sistema de Gestão"

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; padding: 0.5rem 0 1.2rem 0;">
            {logo_html}
            <div>
                <div style="font-weight:700; font-size:1.05rem; line-height:1.1;">{_nome_exibido}</div>
                <div style="font-size:0.75rem; opacity:0.85;">{_subtitulo}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = [
        "Início",
        "Pacientes",
        "Agenda",
        "Relatórios",
        "Configurações",
    ]
    for nome in menu:
        if st.button(nome, key=f"nav_{nome}", use_container_width=True):
            st.session_state.pagina = nome
            st.session_state.editando_id = None

    st.markdown("<div style='flex-grow:1;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.button("Ajuda", use_container_width=True)


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
        consultas_hoje = contar_consultas_hoje(date.today().isoformat())
        st.markdown(
            f"<div class='cv-metric'><div style='color:#6b7c93; font-size:0.85rem;'>Consultas Hoje</div>"
            f"<div style='font-size:1.8rem; font-weight:700; color:#1596ac;'>{consultas_hoje}</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        todas_consultas = listar_consultas()
        pendentes = len([c for c in todas_consultas if c["status"] == "Agendada"])
        st.markdown(
            f"<div class='cv-metric'><div style='color:#6b7c93; font-size:0.85rem;'>Consultas Pendentes</div>"
            f"<div style='font-size:1.8rem; font-weight:700; color:#1596ac;'>{pendentes}</div></div>",
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

        c4, c5, = st.columns(2)
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
        c6, c7 = st.columns(2)
        cep = c6.text_input("CEP", value=dados_atuais.get("cep", ""), placeholder="00000-000")
        logradouro = c7.text_input(
            "Logradouro", value=dados_atuais.get("logradouro", ""), placeholder="Rua, Avenida, etc."
        )

        c8, c9, c10 = st.columns(3)
        numero = c8.text_input("Número", value=dados_atuais.get("numero", ""), placeholder="Nº")
        complemento = c9.text_input(
            "Complemento", value=dados_atuais.get("complemento", ""), placeholder="Apto, Sala, etc."
        )
        bairro = c10.text_input("Bairro", value=dados_atuais.get("bairro", ""))

        c11, c12 = st.columns(2)
        cidade = c11.text_input("Cidade", value=dados_atuais.get("cidade", ""))
        estado_opcoes = ["Selecione"] + ESTADOS_BR
        estado_idx = (
            estado_opcoes.index(dados_atuais["estado"]) if dados_atuais.get("estado") in estado_opcoes else 0
        )
        estado = c12.selectbox("Estado", estado_opcoes, index=estado_idx)

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
# Página: Agenda
# ------------------------------------------------------------------
def pagina_agenda():
    st.title("Agenda")
    st.markdown("<p class='cv-subtitulo'>Gerencie as consultas dos pacientes</p>", unsafe_allow_html=True)
    st.write("")

    aba_nova, aba_lista = st.tabs(["➕ Nova Consulta", "📆 Consultas"])

    with aba_nova:
        pacientes = listar_pacientes()
        if not pacientes:
            st.warning("Cadastre ao menos um paciente antes de agendar uma consulta.")
        else:
            opcoes = {f"{p['nome_completo']} (CPF: {p['cpf']})": p["id"] for p in pacientes}
            with st.form("form_consulta", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                paciente_label = c1.selectbox("Paciente*", list(opcoes.keys()))
                data_consulta = c2.date_input("Data*", value=date.today(), format="DD/MM/YYYY")
                hora_consulta = c3.time_input("Hora*", value=datetime.now().time().replace(second=0, microsecond=0))

                c4, c5 = st.columns(2)
                tipo = c4.selectbox(
                    "Tipo de Consulta", ["Consulta de Rotina", "Retorno", "Exame", "Urgência"]
                )
                medico = c5.text_input("Médico(a) Responsável", placeholder="Dr(a). Nome")
                obs = st.text_area("Observações", placeholder="Alguma observação sobre a consulta")

                if st.form_submit_button("Agendar Consulta", type="primary"):
                    dados = {
                        "paciente_id": opcoes[paciente_label],
                        "data": data_consulta.isoformat(),
                        "hora": hora_consulta.strftime("%H:%M"),
                        "tipo": tipo,
                        "medico": medico.strip(),
                        "observacoes": obs.strip(),
                    }
                    sucesso, msg = inserir_consulta(dados)
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with aba_lista:
        filtro_data = st.date_input(
            "Filtrar por data", value=None, format="DD/MM/YYYY", key="filtro_agenda"
        )
        consultas = listar_consultas(filtro_data.isoformat() if filtro_data else None)

        if not consultas:
            st.info("Nenhuma consulta encontrada.")
        else:
            status_cores = {
                "Agendada": "🟡", "Confirmada": "🟢", "Concluída": "🔵", "Cancelada": "🔴"
            }
            for c in consultas:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y")
                    col1.markdown(f"**{c['nome_completo']}**  \n{c['tipo'] or '—'}")
                    col2.markdown(f"📅 {data_fmt} às {c['hora']}  \n👨‍⚕️ {c['medico'] or '—'}")

                    status_atual = c["status"]
                    novo_status = col3.selectbox(
                        "Status",
                        list(status_cores.keys()),
                        index=list(status_cores.keys()).index(status_atual),
                        key=f"status_{c['id']}",
                        label_visibility="collapsed",
                    )
                    if novo_status != status_atual:
                        atualizar_status_consulta(c["id"], novo_status)
                        st.rerun()

                    if c.get("observacoes"):
                        st.caption(f"📝 {c['observacoes']}")

                    if st.button("🗑️ Cancelar/Excluir", key=f"del_consulta_{c['id']}"):
                        excluir_consulta(c["id"])
                        st.rerun()


# ------------------------------------------------------------------
# Página: Relatórios
# ------------------------------------------------------------------
def pagina_relatorios():
    st.title("Relatórios")
    st.markdown("<p class='cv-subtitulo'>Visão analítica dos dados da clínica</p>", unsafe_allow_html=True)
    st.write("")

    pacientes = listar_pacientes()
    consultas = listar_consultas()

    if not pacientes:
        st.info("Cadastre pacientes para visualizar relatórios.")
        return

    df_pac = pd.DataFrame(pacientes)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pacientes por Sexo")
        if df_pac["sexo"].replace("", pd.NA).notna().any():
            contagem_sexo = df_pac["sexo"].replace("", "Não informado").value_counts().reset_index()
            contagem_sexo.columns = ["Sexo", "Total"]
            fig = px.pie(
                contagem_sexo, names="Sexo", values="Total", hole=0.5,
                color_discrete_sequence=["#1596ac", "#66c2d4", "#0d7c90", "#a3dbe6"],
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de sexo cadastrados.")

    with col2:
        st.subheader("Pacientes por Estado")
        if df_pac["estado"].replace("", pd.NA).notna().any():
            contagem_estado = df_pac["estado"].replace("", "Não informado").value_counts().reset_index()
            contagem_estado.columns = ["Estado", "Total"]
            fig = px.bar(
                contagem_estado, x="Estado", y="Total",
                color_discrete_sequence=["#1596ac"],
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de estado cadastrados.")

    st.write("")
    st.subheader("Consultas por Status")
    if consultas:
        df_con = pd.DataFrame(consultas)
        contagem_status = df_con["status"].value_counts().reset_index()
        contagem_status.columns = ["Status", "Total"]
        fig = px.bar(
            contagem_status, x="Status", y="Total", color="Status",
            color_discrete_map={
                "Agendada": "#f4b400", "Confirmada": "#0f9d58",
                "Concluída": "#1596ac", "Cancelada": "#db4437",
            },
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma consulta registrada ainda.")

    st.write("")
    st.subheader("Exportar dados")
    col_a, col_b = st.columns(2)
    csv_pacientes = df_pac.to_csv(index=False).encode("utf-8-sig")
    col_a.download_button(
        "⬇️ Baixar Pacientes (CSV)", data=csv_pacientes,
        file_name="pacientes_clinica_vida.csv", mime="text/csv",
        use_container_width=True,
    )
    if consultas:
        csv_consultas = pd.DataFrame(consultas).to_csv(index=False).encode("utf-8-sig")
        col_b.download_button(
            "⬇️ Baixar Consultas (CSV)", data=csv_consultas,
            file_name="consultas_clinica_vida.csv", mime="text/csv",
            use_container_width=True,
        )


# ------------------------------------------------------------------
# Página: Configurações
# ------------------------------------------------------------------
def pagina_configuracoes():
    st.title("Configurações")
    st.markdown("<p class='cv-subtitulo'>Preferências do sistema</p>", unsafe_allow_html=True)
    st.write("")

    cfg = st.session_state.config

    # ----------------------------------------------------------
    # Dados da Clínica (nome, telefone, e-mail, endereço, filial)
    # ----------------------------------------------------------
    st.subheader("🏥 Dados da Clínica")
    with st.form("form_config_clinica"):
        c1, c2 = st.columns(2)
        nome_clinica = c1.text_input("Nome da Clínica", value=cfg.get("nome_clinica", "Clínica PTF"))
        telefone = c2.text_input(
            "Telefone de Contato", value=cfg.get("telefone_clinica", ""),
            placeholder="(00) 00000-0000",
        )

        c3, c4 = st.columns(2)
        email_clinica = c3.text_input(
            "E-mail da Clínica", value=cfg.get("email_clinica", ""),
            placeholder="contato@clinica.com.br",
        )
        endereco_clinica = c4.text_input(
            "Endereço", value=cfg.get("endereco_clinica", ""),
            placeholder="Rua, número, bairro, cidade",
        )

        st.markdown("**📍 Filial**")
        c5, c6 = st.columns(2)
        estado_opcoes = ["Selecione"] + ESTADOS_BR
        estado_salvo = cfg.get("filial_estado", "Selecione")
        estado_idx = estado_opcoes.index(estado_salvo) if estado_salvo in estado_opcoes else 0
        filial_estado = c5.selectbox("Estado da Filial", estado_opcoes, index=estado_idx)
        filial_cidade = c6.text_input("Cidade da Filial", value=cfg.get("filial_cidade", ""))

        if st.form_submit_button("Salvar Dados da Clínica", type="primary"):
            if email_clinica.strip() and not validar_email(email_clinica):
                st.error("E-mail inválido. Verifique o formato digitado.")
            else:
                novas = {
                    "nome_clinica": nome_clinica.strip(),
                    "telefone_clinica": telefone.strip(),
                    "email_clinica": email_clinica.strip(),
                    "endereco_clinica": endereco_clinica.strip(),
                    "filial_estado": filial_estado,
                    "filial_cidade": filial_cidade.strip(),
                }
                salvar_configuracoes(novas)
                st.session_state.config.update(novas)
                st.success("Dados da clínica salvos com sucesso!")
                st.rerun()

    # ----------------------------------------------------------
    # Acessibilidade
    # ----------------------------------------------------------
    st.write("")
    st.subheader("♿ Acessibilidade")
    with st.form("form_config_acessibilidade"):
        tamanho_fonte = st.slider(
            "Tamanho da fonte (%)",
            min_value=80, max_value=150,
            value=int(cfg.get("tamanho_fonte", "100")),
            step=10,
            help="Ajusta o tamanho de todo o texto do sistema.",
        )

        c7, c8 = st.columns(2)
        alto_contraste = c7.checkbox(
            "Alto contraste",
            value=cfg.get("alto_contraste", "False") == "True",
            help="Aumenta o contraste de cores para facilitar a leitura.",
        )
        reduzir_animacoes = c8.checkbox(
            "Reduzir animações",
            value=cfg.get("reduzir_animacoes", "False") == "True",
            help="Desativa transições e animações da interface.",
        )

        tema_opcoes = ["Compacto", "Confortável"]
        tema_salvo = cfg.get("tema_tabela", "Confortável")
        tema_idx = tema_opcoes.index(tema_salvo) if tema_salvo in tema_opcoes else 1
        tema_tabela = st.radio("Espaçamento das listas", tema_opcoes, index=tema_idx, horizontal=True)

        if st.form_submit_button("Salvar Acessibilidade", type="primary"):
            novas = {
                "tamanho_fonte": str(tamanho_fonte),
                "alto_contraste": str(alto_contraste),
                "reduzir_animacoes": str(reduzir_animacoes),
                "tema_tabela": tema_tabela,
            }
            salvar_configuracoes(novas)
            st.session_state.config.update(novas)
            st.success("Preferências de acessibilidade salvas!")
            st.rerun()

    st.write("")
    st.subheader("💾 Banco de Dados")
    total_pac = contar_pacientes()
    st.write(f"O sistema utiliza um banco **SQLite local** (`clinica_vida.db`) com **{total_pac}** paciente(s) cadastrado(s).")
    st.caption("Para reiniciar o sistema do zero, apague o arquivo `clinica_vida.db` na pasta do projeto.")


# ------------------------------------------------------------------
# Roteamento
# ------------------------------------------------------------------
pagina = st.session_state.pagina
if pagina == "Início":
    pagina_inicio()
elif pagina == "Pacientes":
    pagina_pacientes()
elif pagina == "Agenda":
    pagina_agenda()
elif pagina == "Relatórios":
    pagina_relatorios()
elif pagina == "Configurações":
    pagina_configuracoes()
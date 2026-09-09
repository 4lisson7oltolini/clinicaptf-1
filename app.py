import base64
from pathlib import Path

import streamlit as st
from PIL import Image

from database import init_db, obter_todas_configuracoes
from modules.agenda import pagina_agenda
from modules.auth import tela_login
from modules.help import pagina_ajuda
from modules.home import pagina_inicio
from modules.patients import pagina_pacientes
from modules.reports import pagina_relatorios
from modules.settings import pagina_configuracoes
from modules.styles import apply_accessibility_styles, apply_default_styles


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
    "modo_escuro": "False",
    "empresa_suporte": "",
    "telefone_suporte": "",
    "email_suporte": "",
    "site_suporte": "",
    "horario_suporte": "",
}

if "config" not in st.session_state:
    salvas = obter_todas_configuracoes()
    st.session_state.config = {**_DEFAULTS_CONFIG, **salvas}

cfg = st.session_state.config

_LOGO_PATH = Path(__file__).parent / "assets" / "logo_small.png"
_pagina_icone = "🏥"
if _LOGO_PATH.exists():
    try:
        _pagina_icone = Image.open(_LOGO_PATH)
    except Exception:
        _pagina_icone = "🏥"

st.set_page_config(
    page_title=f"{cfg.get('nome_clinica', 'Clínica PTF')} - Sistema de Gestão",
    page_icon=_pagina_icone,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def carregar_logo_base64():
    if _LOGO_PATH.exists():
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode("utf-8")
    return None


logo_base64 = carregar_logo_base64()

if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"
if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

apply_default_styles()
apply_accessibility_styles(cfg)

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if st.session_state.usuario_logado is None:
    tela_login(logo_base64=logo_base64)
    st.stop()

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

    menu = ["Início", "Pacientes", "Agenda", "Relatórios", "Configurações"]
    for nome in menu:
        if st.button(nome, key=f"nav_{nome}", use_container_width=True):
            st.session_state.pagina = nome
            st.session_state.editando_id = None

    st.markdown("<div style='flex-grow:1;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    _usuario_atual = st.session_state.usuario_logado
    st.markdown(
        f"<div style='font-size:0.8rem; line-height:1.4; padding-bottom:0.4rem;'>"
        f"👤 {_usuario_atual['nome_completo']}<br>"
        f"<span style='opacity:0.75;'>{_usuario_atual['papel']}</span></div>",
        unsafe_allow_html=True,
    )
    if st.button("Sair", use_container_width=True, key="btn_logout"):
        st.session_state.usuario_logado = None
        st.session_state.pagina = "Início"
        st.session_state.editando_id = None
        st.rerun()

    if st.button("Ajuda", use_container_width=True, key="nav_Ajuda"):
        st.session_state.pagina = "Ajuda"
        st.session_state.editando_id = None


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
elif pagina == "Ajuda":
    pagina_ajuda()

import streamlit as st


def apply_default_styles():
    st.markdown(
        """
        <style>
        :root {
            --azul-principal: #1596ac;
            --azul-escuro: #0d7c90;
            --azul-claro: #e6f7ec;
        }

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


def apply_accessibility_styles(cfg):
    _tamanho_fonte = cfg.get("tamanho_fonte", "100")
    _alto_contraste = cfg.get("alto_contraste", "False") == "True"
    _reduzir_animacoes = cfg.get("reduzir_animacoes", "False") == "True"
    _modo_escuro = cfg.get("modo_escuro", "False") == "True"

    _css_acessibilidade = f"""
    <style>
    html {{
        font-size: {_tamanho_fonte}% !important;
    }}
    """

    if _modo_escuro and not _alto_contraste:
        _css_acessibilidade += """
    .stApp {
        background-color: #0e1117 !important;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {
        color: #e5e7eb !important;
    }
    h1, h2, h3, h4 {
        color: #f3f4f6 !important;
    }
    .cv-subtitulo {
        color: #9ca3af !important;
    }
    div[data-testid="stForm"], .cv-metric, div[data-testid="stExpander"],
    div[data-testid="stTabs"], div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1a1f2b !important;
        border-color: #313847 !important;
    }
    input, textarea, select,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] {
        background-color: #1a1f2b !important;
        color: #e5e7eb !important;
        border-color: #3b4252 !important;
    }
    .stButton > button {
        background-color: #1a1f2b !important;
        color: #e5e7eb !important;
        border-color: #3b4252 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--azul-principal) !important;
        border-color: var(--azul-principal) !important;
        color: #ffffff !important;
    }
    div[data-testid="stDataFrame"] {
        background-color: #1a1f2b !important;
    }
    hr {
        border-color: #313847 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f5766 0%, #051f26 100%) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }
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

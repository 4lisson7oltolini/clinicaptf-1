import streamlit as st

from database import (
    contar_usuarios,
    criar_usuario,
    obter_usuario_por_login,
)
from utils import hash_senha, verificar_senha

def ensure_auth_state():
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None


def tela_login(logo_base64=None):
    """Exibe a tela de login (ou de criação do primeiro administrador)."""
    cfg = st.session_state.config
    ensure_auth_state()

    st.markdown("<div style='max-width:420px; margin: 3rem auto 0 auto;'>", unsafe_allow_html=True)

    if logo_base64:
        st.markdown(
            f'<div style="text-align:center; margin-bottom:0.5rem;">'
            f'<img src="data:image/png;base64,{logo_base64}" style="width:64px; height:64px;" /></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f"<h2 style='text-align:center; margin-bottom:0;'>{cfg.get('nome_clinica', 'Clínica PTF')}</h2>"
        f"<p style='text-align:center; color:#6b7c93; margin-top:0;'>Sistema de Gestão</p>",
        unsafe_allow_html=True,
    )
    st.write("")

    if contar_usuarios() == 0:
        st.info("Primeiro acesso: crie a conta de administrador do sistema.")
        with st.form("form_primeiro_admin"):
            nome_completo = st.text_input("Seu nome completo")
            usuario = st.text_input("Usuário (login)", placeholder="ex: admin")
            senha = st.text_input("Senha", type="password", help="Mínimo de 6 caracteres.")
            confirmar = st.text_input("Confirmar senha", type="password")
            if st.form_submit_button("Criar conta e entrar", type="primary", use_container_width=True):
                if not nome_completo.strip() or not usuario.strip():
                    st.error("Preencha seu nome e um usuário de login.")
                elif len(senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif senha != confirmar:
                    st.error("As senhas não conferem.")
                else:
                    senha_hash, salt = hash_senha(senha)
                    sucesso, msg = criar_usuario(
                        usuario, senha_hash, salt, nome_completo, papel="Administrador"
                    )
                    if sucesso:
                        novo = obter_usuario_por_login(usuario)
                        st.session_state.usuario_logado = {
                            "id": novo["id"], "usuario": novo["usuario"],
                            "nome_completo": novo["nome_completo"], "papel": novo["papel"],
                        }
                        st.rerun()
                    else:
                        st.error(msg)
    else:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                dados_usuario = obter_usuario_por_login(usuario)
                if dados_usuario and verificar_senha(senha, dados_usuario["senha_hash"], dados_usuario["salt"]):
                    st.session_state.usuario_logado = {
                        "id": dados_usuario["id"], "usuario": dados_usuario["usuario"],
                        "nome_completo": dados_usuario["nome_completo"], "papel": dados_usuario["papel"],
                    }
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

    st.markdown("</div>", unsafe_allow_html=True)

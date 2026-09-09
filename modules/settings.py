import streamlit as st

from database import (
    atualizar_senha_usuario,
    contar_pacientes,
    contar_usuarios,
    criar_usuario,
    excluir_usuario,
    listar_usuarios,
    obter_usuario_por_id,
    salvar_configuracoes,
)
from utils import ESTADOS_BR, hash_senha, validar_email, verificar_senha


def pagina_configuracoes():
    st.title("Configurações")
    st.markdown("<p class='cv-subtitulo'>Preferências do sistema</p>", unsafe_allow_html=True)
    st.write("")

    cfg = st.session_state.config

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

        c7, c8, c9 = st.columns(3)
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
        modo_escuro = c9.checkbox(
            "🌙 Modo escuro",
            value=cfg.get("modo_escuro", "False") == "True",
            help="Usa um tema escuro em toda a interface. Se o alto contraste estiver ativo, ele tem prioridade.",
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
                "modo_escuro": str(modo_escuro),
                "tema_tabela": tema_tabela,
            }
            salvar_configuracoes(novas)
            st.session_state.config.update(novas)
            st.success("Preferências de acessibilidade salvas!")
            st.rerun()

    st.write("")
    st.subheader("👤 Minha Conta")
    usuario_logado = st.session_state.usuario_logado
    st.write(
        f"Logado como **{usuario_logado['nome_completo']}** "
        f"(usuário `{usuario_logado['usuario']}`, papel: {usuario_logado['papel']})."
    )
    with st.form("form_trocar_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        c_s1, c_s2 = st.columns(2)
        nova_senha = c_s1.text_input("Nova senha", type="password", help="Mínimo de 6 caracteres.")
        confirmar_nova = c_s2.text_input("Confirmar nova senha", type="password")
        if st.form_submit_button("Alterar Senha", type="primary"):
            dados_usuario = obter_usuario_por_id(usuario_logado["id"])
            if not dados_usuario or not verificar_senha(senha_atual, dados_usuario["senha_hash"], dados_usuario["salt"]):
                st.error("Senha atual incorreta.")
            elif len(nova_senha) < 6:
                st.error("A nova senha deve ter pelo menos 6 caracteres.")
            elif nova_senha != confirmar_nova:
                st.error("As senhas não conferem.")
            else:
                novo_hash, novo_salt = hash_senha(nova_senha)
                atualizar_senha_usuario(usuario_logado["id"], novo_hash, novo_salt)
                st.success("Senha alterada com sucesso!")

    if usuario_logado["papel"] == "Administrador":
        st.write("")
        st.subheader("👥 Usuários do Sistema")

        with st.expander("➕ Adicionar novo usuário"):
            with st.form("form_novo_usuario", clear_on_submit=True):
                c_u1, c_u2 = st.columns(2)
                novo_nome = c_u1.text_input("Nome completo")
                novo_login = c_u2.text_input("Usuário (login)")
                c_u3, c_u4 = st.columns(2)
                nova_senha_usuario = c_u3.text_input("Senha", type="password", help="Mínimo de 6 caracteres.")
                novo_papel = c_u4.selectbox("Papel", ["Atendente", "Administrador"])
                if st.form_submit_button("Criar Usuário", type="primary"):
                    if not novo_nome.strip() or not novo_login.strip():
                        st.error("Preencha nome e usuário.")
                    elif len(nova_senha_usuario) < 6:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    else:
                        h, s = hash_senha(nova_senha_usuario)
                        sucesso, msg = criar_usuario(novo_login, h, s, novo_nome, papel=novo_papel)
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        usuarios = listar_usuarios()
        for u in usuarios:
            with st.container(border=True):
                c_l1, c_l2 = st.columns([4, 1])
                c_l1.markdown(f"**{u['nome_completo']}**  \n`{u['usuario']}` · {u['papel']}")
                eh_o_proprio = u["id"] == usuario_logado["id"]
                eh_ultimo_admin = u["papel"] == "Administrador" and contar_usuarios(papel="Administrador") <= 1
                if eh_o_proprio:
                    c_l2.caption("Você")
                elif eh_ultimo_admin:
                    c_l2.caption("Único admin")
                else:
                    if c_l2.button("🗑️ Remover", key=f"excluir_usuario_{u['id']}"):
                        excluir_usuario(u["id"])
                        st.rerun()

        st.write("")
        st.subheader("🛠️ Suporte Técnico")
        st.caption("Esses dados aparecem para todos os usuários na página de Ajuda.")
        with st.form("form_config_suporte"):
            c_sp1, c_sp2 = st.columns(2)
            empresa_suporte = c_sp1.text_input(
                "Empresa responsável pela manutenção", value=cfg.get("empresa_suporte", "")
            )
            telefone_suporte = c_sp2.text_input(
                "Telefone / WhatsApp", value=cfg.get("telefone_suporte", ""),
                placeholder="(00) 00000-0000",
            )
            c_sp3, c_sp4 = st.columns(2)
            email_suporte = c_sp3.text_input(
                "E-mail de suporte", value=cfg.get("email_suporte", ""),
                placeholder="suporte@empresa.com.br",
            )
            site_suporte = c_sp4.text_input(
                "Site / Link de atendimento", value=cfg.get("site_suporte", ""),
                placeholder="https://...",
            )
            horario_suporte = st.text_input(
                "Horário de atendimento", value=cfg.get("horario_suporte", ""),
                placeholder="Seg. a Sex., 9h às 18h",
            )
            if st.form_submit_button("Salvar Contato de Suporte", type="primary"):
                if email_suporte.strip() and not validar_email(email_suporte):
                    st.error("E-mail de suporte inválido. Verifique o formato digitado.")
                else:
                    novas = {
                        "empresa_suporte": empresa_suporte.strip(),
                        "telefone_suporte": telefone_suporte.strip(),
                        "email_suporte": email_suporte.strip(),
                        "site_suporte": site_suporte.strip(),
                        "horario_suporte": horario_suporte.strip(),
                    }
                    salvar_configuracoes(novas)
                    st.session_state.config.update(novas)
                    st.success("Contato de suporte salvo com sucesso!")
                    st.rerun()

    st.write("")
    st.subheader("💾 Banco de Dados")
    total_pac = contar_pacientes()
    st.write(f"O sistema utiliza um banco **SQLite local** (`clinica_vida.db`) com **{total_pac}** paciente(s) cadastrado(s).")
    st.caption("Para reiniciar o sistema do zero, apague o arquivo `clinica_vida.db` na pasta do projeto.")

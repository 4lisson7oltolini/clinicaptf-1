import streamlit as st


def pagina_ajuda():
    st.title("Ajuda")
    st.markdown("<p class='cv-subtitulo'>Guia de uso do sistema e contato do suporte</p>", unsafe_allow_html=True)
    st.write("")

    abas = st.tabs([
        "🚀 Primeiros Passos",
        "🧑‍🤝‍🧑 Pacientes",
        "📅 Agenda",
        "📄 Relatórios",
        "⚙️ Configurações",
        "❓ Perguntas Frequentes",
        "📞 Suporte Técnico",
    ])

    with abas[0]:
        st.subheader("Primeiros Passos")
        st.markdown(
            """
1. **Login**: use o usuário e senha cadastrados para entrar. Se você não tem um usuário, peça a um Administrador do sistema para criar um para você.
2. **Menu lateral**: use os botões à esquerda (Início, Pacientes, Agenda, Relatórios, Configurações) para
   navegar entre as áreas do sistema.
3. **Início**: mostra um resumo com o total de pacientes, consultas do dia, consultas pendentes e os
   últimos pacientes cadastrados.
4. **Sair**: use o botão "Sair", no final do menu lateral, para encerrar sua sessão com segurança.
            """
        )

    with abas[1]:
        st.subheader("Cadastrar e gerenciar Pacientes")
        st.markdown(
            """
1. Vá em **Pacientes** no menu lateral e abra a aba **Cadastro**.
2. Preencha nome, data de nascimento, CPF e os demais dados pessoais.
3. No campo **CEP**, digite o CEP do paciente e clique em **"🔍 Buscar endereço pelo CEP"** — o sistema
   preenche automaticamente Logradouro, Bairro, Cidade e Estado.
4. Clique em **Salvar** para concluir o cadastro.
5. Na aba **Lista de Pacientes**, use o campo de busca para encontrar um paciente por nome ou CPF.
6. Use os botões **✏️ Editar** ou **🗑️ Excluir** em cada paciente para alterar ou remover o cadastro.
            """
        )

    with abas[2]:
        st.subheader("Agenda de Consultas")
        st.markdown(
            """
1. Vá em **Agenda** e abra a aba **Nova Consulta**.
2. Selecione o paciente (já deve estar cadastrado), a data, a hora, o tipo de consulta e o médico
   responsável.
3. Clique em **Agendar Consulta**.
4. Na aba **Consultas**, veja todas as consultas agendadas, filtre por data e altere o **status**
   (Agendada, Confirmada, Concluída ou Cancelada) diretamente na lista.
5. Use **🗑️ Cancelar/Excluir** para remover uma consulta.
            """
        )

    with abas[3]:
        st.subheader("Relatórios")
        st.markdown(
            """
1. Vá em **Relatórios** para ver gráficos com a distribuição de pacientes por sexo e por estado, além
   das consultas por status.
2. No final da página, use os botões **⬇️ Baixar Pacientes (CSV)** e **⬇️ Baixar Consultas (CSV)** para
   exportar os dados e abrir em Excel ou Google Planilhas.
            """
        )

    with abas[4]:
        st.subheader("Configurações")
        st.markdown(
            """
- **Dados da Clínica**: nome, telefone, e-mail e endereço. Esses dados aparecem no menu lateral e no
  título do sistema.
- **Filial**: selecione o estado e a cidade da unidade — aparece logo abaixo do nome da clínica no menu.
- **Acessibilidade**: ajuste o tamanho da fonte, ative o alto contraste, o **modo escuro** ou reduza as
  animações da interface.
- **Minha Conta**: qualquer usuário pode trocar a própria senha aqui.
- **Usuários** *(somente Administradores)*: criar novos usuários (Administrador ou Atendente) e remover
  usuários existentes.
- **Suporte Técnico** *(somente Administradores)*: cadastrar o contato da empresa responsável pela
  manutenção do sistema, exibido para todos na aba **Suporte Técnico** desta página de Ajuda.
            """
        )

    with abas[5]:
        st.subheader("Perguntas Frequentes")
        with st.expander("Esqueci minha senha, e agora?"):
            st.write(
                "Fale com um Administrador do sistema — ele pode removê-lo(a) e criar um novo usuário "
                "para você em **Configurações → Usuários**. Ainda não existe um recurso de recuperação "
                "automática de senha."
            )
        with st.expander("Como eu ativo o modo escuro?"):
            st.write("Vá em **Configurações → Acessibilidade** e marque a opção **🌙 Modo escuro**.")
        with st.expander("Como adiciono um novo usuário ao sistema?"):
            st.write(
                "Somente Administradores conseguem fazer isso, em **Configurações → Usuários → "
                "➕ Adicionar novo usuário**."
            )
        with st.expander("O autopreenchimento pelo CEP não funcionou, o que fazer?"):
            st.write(
                "Confira se o CEP tem 8 dígitos e se o computador está com internet. Se o problema "
                "persistir, entre em contato com o suporte técnico (aba ao lado)."
            )
        with st.expander("Meus dados ficam salvos onde?"):
            st.write(
                "Tudo é salvo localmente em um banco de dados SQLite (`clinica_vida.db`), na mesma pasta "
                "do sistema."
            )

    with abas[6]:
        st.subheader("Suporte Técnico")
        empresa = st.session_state.config.get("empresa_suporte", "")
        telefone = st.session_state.config.get("telefone_suporte", "")
        email_sup = st.session_state.config.get("email_suporte", "")
        site = st.session_state.config.get("site_suporte", "")
        horario = st.session_state.config.get("horario_suporte", "")

        if not any([empresa, telefone, email_sup, site]):
            st.info(
                "O contato do suporte técnico ainda não foi configurado. "
                "Um Administrador pode preenchê-lo em **Configurações → Suporte Técnico**."
            )
        else:
            with st.container(border=True):
                if empresa:
                    st.markdown(f"**Empresa responsável:** {empresa}")
                if telefone:
                    st.markdown(f"**Telefone / WhatsApp:** {telefone}")
                if email_sup:
                    st.markdown(f"**E-mail:** {email_sup}")
                if site:
                    st.markdown(f"**Site / Atendimento:** {site}")
                if horario:
                    st.markdown(f"**Horário de atendimento:** {horario}")

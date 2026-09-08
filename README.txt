# Clínica Vida - Sistema de Gestão

Dashboard em Streamlit para cadastro e gestão de pacientes, inspirado no layout de referência (menu lateral azul/teal).

## Estrutura

```
clinica_vida/
├── app.py            # App principal (interface e páginas)
├── database.py        # Camada de acesso ao banco (SQLite)
├── utils.py            # Validação de CPF, formatação de CEP/CPF
├── assets/
│   └── logo_small.png  # Logo da clínica, exibida no menu lateral
└── requirements.txt    # Dependências
```

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

Um arquivo `clinica_vida.db` (SQLite) será criado automaticamente na primeira execução — não precisa configurar nada.

## Funcionalidades

- **Login**: acesso protegido por usuário e senha (senhas nunca são salvas em texto puro — usam hash PBKDF2-HMAC-SHA256 com salt aleatório). No primeiro acesso (banco vazio), o sistema pede a criação da conta de administrador.
- **Início**: métricas gerais (total de pacientes, consultas do dia, pendentes) e últimos cadastros.
- **Pacientes**:
  - Cadastro com validação de CPF (algoritmo de dígitos verificadores) e bloqueio de CPF duplicado.
  - **Autopreenchimento de endereço pelo CEP** (via API ViaCEP): digite o CEP e clique em "Buscar endereço pelo CEP" para preencher automaticamente logradouro, bairro, cidade e estado.
  - Edição e exclusão de pacientes.
  - Busca por nome ou CPF.
- **Agenda**:
  - Agendamento de consultas vinculadas a um paciente (data, hora, tipo, médico).
  - Alteração de status (Agendada, Confirmada, Concluída, Cancelada) direto na lista.
  - Filtro por data.
- **Relatórios**:
  - Gráfico de pacientes por sexo (pizza) e por estado (barras).
  - Gráfico de consultas por status.
  - Exportação de pacientes e consultas em CSV.
- **Configurações**:
  - Dados da clínica: nome, telefone, e-mail (validado) e endereço — persistidos no banco.
  - Filial: seleção de estado (UF) e cidade, exibida no menu lateral.
  - Acessibilidade: tamanho da fonte (80%–150%), alto contraste, **modo escuro**, redução de animações e espaçamento das listas — aplicado em tempo real na interface.
  - Minha Conta: troca da própria senha.
  - Usuários (apenas Administradores): criar novos usuários (Administrador ou Atendente) e remover usuários existentes.
  - Informações do banco de dados.

## Próximos passos sugeridos

- Autenticação de usuários (ex: `streamlit-authenticator`).
- Deploy no Streamlit Community Cloud ou em um servidor próprio.
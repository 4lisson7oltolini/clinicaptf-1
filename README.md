# Clínica PTF - Sistema de Gestão

Aplicação web em Streamlit para gestão de clínica, com cadastro e acompanhamento de pacientes, agendamento de consultas, relatórios e configurações da clínica.

A estrutura foi reorganizada para separar a lógica por responsabilidade, em vez de manter tudo em um único arquivo `app.py`.

## Visão geral

Este projeto foi evoluído de uma base monolítica para uma estrutura modular, com uma entrada principal responsável por:

- inicializar o banco SQLite;
- carregar as configurações salvas;
- montar o menu lateral;
- aplicar estilos globais;
- controlar login/sessão do usuário;
- direcionar para as páginas por módulo.

Com isso, a manutenção ficou mais simples, especialmente para crescer com novas telas e regras de negócio.

## Estrutura do projeto

```text
clinicaptf-1/
├── app.py                  # Entrada principal da aplicação
├── database.py            # Banco SQLite e operações CRUD
├── utils.py               # Utilitários gerais (CPF, CEP, hashing, validações)
├── requirements.txt       # Dependências do projeto
├── clinica_vida.db        # Banco local SQLite (criado automaticamente)
├── assets/
│   └── logo_small.png     # Logo exibida no menu lateral
├── modules/
│   ├── __init__.py
│   ├── auth.py            # Tela de login e criação do primeiro administrador
│   ├── home.py            # Dashboard inicial / visão geral
│   ├── patients.py        # Cadastro, busca, edição e exclusão de pacientes
│   ├── agenda.py          # Agendamento e controle de consultas
│   ├── reports.py         # Relatórios e exportação CSV
│   ├── settings.py        # Configurações da clínica e usuários
│   ├── help.py            # Página de ajuda e suporte
│   └── styles.py          # Estilos globais e acessibilidade
└── README.md              # Documentação do projeto
```

## Arquitetura modular

A partir da refatoração, a aplicação foi separada em módulos com foco em responsabilidade:

- `app.py`: roteador principal da aplicação
- `modules/auth.py`: autenticação, login e primeiro usuário administrador
- `modules/home.py`: tela inicial com métricas e principais informações
- `modules/patients.py`: gestão de pacientes
- `modules/agenda.py`: agenda e consultas
- `modules/reports.py`: gráficos e exportação
- `modules/settings.py`: clínicas, acessibilidade, usuários e senha
- `modules/help.py`: documentação e suporte interno
- `modules/styles.py`: estilos visuais e ajustes de acessibilidade

Essa divisão facilita a leitura do código, reduz acoplamento e deixa cada tela mais independente.

## Como executar localmente

### 1) Instalar dependências

```bash
pip install -r requirements.txt
```

### 2) Iniciar a aplicação

```bash
streamlit run app.py
```

A aplicação ficará disponível em:

```text
http://localhost:8501
```

### Banco de dados

Por padrão, a aplicação usa o arquivo SQLite:

```text
clinica_vida.db
```

Esse arquivo é criado automaticamente na primeira execução.

Se quiser definir um caminho customizado, é possível usar uma variável de ambiente:

```bash
set CLINICA_DB_PATH=C:\caminho\para\dados\clinica_vida.db
```

ou no Linux/macOS:

```bash
export CLINICA_DB_PATH=/caminho/para/dados/clinica_vida.db
```

## Funcionalidades

### Autenticação e segurança

- Login com usuário e senha
- Primeiro acesso cria automaticamente um administrador
- Senhas armazenadas com hash PBKDF2-HMAC-SHA256 + salt
- Sessão de usuário controlada pelo Streamlit `session_state`

### Tela inicial

- Total de pacientes cadastrados
- Consultas do dia
- Consultas pendentes
- Últimos pacientes cadastrados

### Pacientes

- Cadastro de pacientes
- Validação de CPF
- Bloqueio de CPF duplicado
- Busca por nome ou CPF
- Edição e exclusão
- Autopreenchimento de endereço via CEP (ViaCEP)

### Agenda

- Agendamento de consultas
- Vinculação com paciente
- Campos de data, hora, tipo, médico e observações
- Alteração de status da consulta
- Filtro por data

### Relatórios

- Gráficos por sexo
- Gráficos por estado
- Gráficos por status de consulta
- Exportação de dados em CSV

### Configurações

- Dados da clínica
- Filial (estado e cidade)
- Ajustes de acessibilidade
- Modo escuro
- Tamanho da fonte
- Alto contraste
- Redução de animações
- Minha conta e troca de senha
- Gestão de usuários (administrador e atendente)
- Visualização de informações do banco

### Ajuda e suporte

- Central de ajuda dentro da aplicação
- Conteúdo de suporte para usuários e manutenção do sistema

## Dependências principais

- Streamlit
- SQLite3
- Pandas
- Plotly
- Pillow
- Requests
- PyJWT / outras libs conforme necessário pelo ambiente

## Observações importantes

- A estrutura modular foi criada para facilitar manutenção e crescimento do projeto.
- O arquivo `app.py` agora atua como roteador principal e não concentra todo o código da aplicação.
- O uso do arquivo `CLINICA_DB_PATH` permite adaptar o local do banco conforme o ambiente.

## Próximos passos sugeridos

- Melhorar o sistema de permissões por perfil de usuário
- Adicionar logs e auditoria de ações
- Criar testes automatizados
- Preparar deploy em servidor ou plataforma cloud
- Expandir a página de relatórios com filtros e comparativos por período

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature ou correção
3. Faça o commit das alterações
4. Abra um pull request com descrição clara da mudança

## Licença

Este projeto é destinado a uso interno/educacional e pode ser adaptado conforme a necessidade da clínica ou equipe responsável.

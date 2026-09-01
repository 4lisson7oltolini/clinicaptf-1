#Clínica PTF - Sistema de Gestão#

Dashboard em Streamlit para cadastro e gestão de pacientes, inspirado no layout de referência (menu lateral azul/teal).

## Estrutura
Clinicaptf-1.1/
├── __pycache__/
├── assets/
|      └──logo_small.png  #Logo da Clinica
├── README.TXT
├── app.py                #APP Principal.
├── clinica_vida.db       
├── database.py           #Banco de dados em SQLite.
├── requirements.txt      #Dependencia 
├── utils.py              #Validação de CPF e formatção de CPF e CEP.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

Um arquivo `clinica_vida.db` (SQLite) será criado automaticamente na primeira execução — não precisa configurar nada.

## Funcionalidades

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
  - Acessibilidade: tamanho da fonte (80%–150%), alto contraste, redução de animações e espaçamento das listas — aplicado em tempo real na interface.
  - Informações do banco de dados.

## Próximos passos sugeridos

- Persistir as configurações da clínica em uma tabela `configuracoes` (hoje ficam só na sessão).
- Autenticação de usuários (ex: `streamlit-authenticator`).
- Integração com API de CEP (ex: ViaCEP) para autopreencher endereço.
- Deploy no Streamlit Community Cloud ou em um servidor próprio.

from datetime import date

import pandas as pd
import streamlit as st

from database import (
    atualizar_paciente,
    excluir_paciente,
    inserir_paciente,
    listar_pacientes,
    obter_paciente,
)
from utils import ESTADOS_BR, buscar_endereco_por_cep, formatar_cep, formatar_cpf, validar_cpf


def _chaves_formulario_paciente(pid):
    return [
        f"pac_nome_{pid}", f"pac_data_nasc_{pid}", f"pac_cpf_{pid}", f"pac_rg_{pid}",
        f"pac_sexo_{pid}", f"pac_estado_civil_{pid}", f"pac_cep_{pid}",
        f"pac_logradouro_{pid}", f"pac_numero_{pid}", f"pac_complemento_{pid}",
        f"pac_bairro_{pid}", f"pac_cidade_{pid}", f"pac_estado_{pid}",
    ]


def _limpar_formulario_paciente(pid):
    for chave in _chaves_formulario_paciente(pid):
        st.session_state.pop(chave, None)


def formulario_paciente():
    editando = st.session_state.editando_id is not None
    dados_atuais = obter_paciente(st.session_state.editando_id) if editando else {}
    pid = st.session_state.editando_id if editando else "novo"

    titulo = "Editar Paciente" if editando else "Cadastro de Paciente"
    st.subheader(titulo)
    st.markdown("<p class='cv-subtitulo'>Preencha os dados do paciente</p>", unsafe_allow_html=True)
    st.write("")

    if f"pac_nome_{pid}" not in st.session_state:
        st.session_state[f"pac_nome_{pid}"] = dados_atuais.get("nome_completo", "")
        st.session_state[f"pac_cpf_{pid}"] = dados_atuais.get("cpf", "")
        st.session_state[f"pac_rg_{pid}"] = dados_atuais.get("rg", "")
        st.session_state[f"pac_sexo_{pid}"] = dados_atuais.get("sexo") or "Selecione"
        st.session_state[f"pac_estado_civil_{pid}"] = dados_atuais.get("estado_civil") or "Selecione"
        st.session_state[f"pac_cep_{pid}"] = dados_atuais.get("cep", "")
        st.session_state[f"pac_logradouro_{pid}"] = dados_atuais.get("logradouro", "")
        st.session_state[f"pac_numero_{pid}"] = dados_atuais.get("numero", "")
        st.session_state[f"pac_complemento_{pid}"] = dados_atuais.get("complemento", "")
        st.session_state[f"pac_bairro_{pid}"] = dados_atuais.get("bairro", "")
        st.session_state[f"pac_cidade_{pid}"] = dados_atuais.get("cidade", "")
        st.session_state[f"pac_estado_{pid}"] = dados_atuais.get("estado") or "Selecione"
        try:
            st.session_state[f"pac_data_nasc_{pid}"] = (
                date.fromisoformat(dados_atuais["data_nascimento"])
                if dados_atuais.get("data_nascimento")
                else None
            )
        except ValueError:
            st.session_state[f"pac_data_nasc_{pid}"] = None

    with st.form("form_paciente", clear_on_submit=False):
        st.markdown("**👤 Informações do Paciente**")
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome Completo*", key=f"pac_nome_{pid}")
        data_nasc = c2.date_input(
            "Data de Nascimento",
            key=f"pac_data_nasc_{pid}",
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )
        cpf = c3.text_input("CPF*", key=f"pac_cpf_{pid}", placeholder="000.000.000-00")

        c4, c5 = st.columns(2)
        sexo_opcoes = ["Selecione", "Feminino", "Masculino", "Outro"]
        sexo = c4.selectbox("Sexo", sexo_opcoes, key=f"pac_sexo_{pid}")

        civil_opcoes = ["Selecione", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"]
        estado_civil = c5.selectbox("Estado Civil", civil_opcoes, key=f"pac_estado_civil_{pid}")

        st.markdown("**📍 Endereço**")
        c6, c7 = st.columns([1, 2])
        cep = c6.text_input("CEP*", key=f"pac_cep_{pid}", placeholder="00000-000")
        with c7:
            st.write("")
            buscar_cep = st.form_submit_button("🔍 Buscar endereço pelo CEP", use_container_width=True)

        if buscar_cep:
            sucesso, resultado = buscar_endereco_por_cep(cep)
            if sucesso:
                st.session_state[f"pac_logradouro_{pid}"] = resultado["logradouro"]
                st.session_state[f"pac_bairro_{pid}"] = resultado["bairro"]
                st.session_state[f"pac_cidade_{pid}"] = resultado["localidade"]
                if resultado["uf"] in ESTADOS_BR:
                    st.session_state[f"pac_estado_{pid}"] = resultado["uf"]
                st.success("Endereço encontrado! Confira os campos abaixo.")
            else:
                st.error(resultado)

        logradouro = st.text_input(
            "Logradouro", key=f"pac_logradouro_{pid}", placeholder="Rua, Avenida, etc."
        )

        c8, c9, c10 = st.columns(3)
        numero = c8.text_input("Número", key=f"pac_numero_{pid}", placeholder="Nº")
        complemento = c9.text_input(
            "Complemento", key=f"pac_complemento_{pid}", placeholder="Apto, Sala, etc."
        )
        bairro = c10.text_input("Bairro", key=f"pac_bairro_{pid}")

        c11, c12 = st.columns(2)
        cidade = c11.text_input("Cidade", key=f"pac_cidade_{pid}")
        estado_opcoes = ["Selecione"] + ESTADOS_BR
        estado = c12.selectbox("Estado", estado_opcoes, key=f"pac_estado_{pid}")

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
                    _limpar_formulario_paciente(pid)
                    st.session_state.editando_id = None
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        if cancelar:
            _limpar_formulario_paciente(pid)
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

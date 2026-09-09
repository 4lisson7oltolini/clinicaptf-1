from datetime import date

import pandas as pd
import streamlit as st

from database import contar_consultas_hoje, contar_pacientes, listar_consultas, listar_pacientes


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

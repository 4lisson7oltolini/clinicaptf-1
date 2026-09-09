import pandas as pd
import plotly.express as px
import streamlit as st

from database import listar_consultas, listar_pacientes


def pagina_relatorios():
    st.title("Relatórios")
    st.markdown("<p class='cv-subtitulo'>Visão analítica dos dados da clínica</p>", unsafe_allow_html=True)
    st.write("")

    pacientes = listar_pacientes()
    consultas = listar_consultas()

    if not pacientes:
        st.info("Cadastre pacientes para visualizar relatórios.")
        return

    df_pac = pd.DataFrame(pacientes)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pacientes por Sexo")
        if df_pac["sexo"].replace("", pd.NA).notna().any():
            contagem_sexo = df_pac["sexo"].replace("", "Não informado").value_counts().reset_index()
            contagem_sexo.columns = ["Sexo", "Total"]
            fig = px.pie(
                contagem_sexo, names="Sexo", values="Total", hole=0.5,
                color_discrete_sequence=["#1596ac", "#66c2d4", "#0d7c90", "#a3dbe6"],
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de sexo cadastrados.")

    with col2:
        st.subheader("Pacientes por Estado")
        if df_pac["estado"].replace("", pd.NA).notna().any():
            contagem_estado = df_pac["estado"].replace("", "Não informado").value_counts().reset_index()
            contagem_estado.columns = ["Estado", "Total"]
            fig = px.bar(
                contagem_estado, x="Estado", y="Total",
                color_discrete_sequence=["#1596ac"],
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de estado cadastrados.")

    st.write("")
    st.subheader("Consultas por Status")
    if consultas:
        df_con = pd.DataFrame(consultas)
        contagem_status = df_con["status"].value_counts().reset_index()
        contagem_status.columns = ["Status", "Total"]
        fig = px.bar(
            contagem_status, x="Status", y="Total", color="Status",
            color_discrete_map={
                "Agendada": "#f4b400", "Confirmada": "#0f9d58",
                "Concluída": "#1596ac", "Cancelada": "#db4437",
            },
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma consulta registrada ainda.")

    st.write("")
    st.subheader("Exportar dados")
    col_a, col_b = st.columns(2)
    csv_pacientes = df_pac.to_csv(index=False).encode("utf-8-sig")
    col_a.download_button(
        "⬇️ Baixar Pacientes (CSV)", data=csv_pacientes,
        file_name="pacientes_clinica_vida.csv", mime="text/csv",
        use_container_width=True,
    )
    if consultas:
        csv_consultas = pd.DataFrame(consultas).to_csv(index=False).encode("utf-8-sig")
        col_b.download_button(
            "⬇️ Baixar Consultas (CSV)", data=csv_consultas,
            file_name="consultas_clinica_vida.csv", mime="text/csv",
            use_container_width=True,
        )

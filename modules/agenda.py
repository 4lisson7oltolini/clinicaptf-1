from datetime import date, datetime

import streamlit as st

from database import (
    excluir_consulta,
    inserir_consulta,
    listar_consultas,
    listar_pacientes,
    atualizar_status_consulta,
)


def pagina_agenda():
    st.title("Agenda")
    st.markdown("<p class='cv-subtitulo'>Gerencie as consultas dos pacientes</p>", unsafe_allow_html=True)
    st.write("")

    aba_nova, aba_lista = st.tabs(["➕ Nova Consulta", "📆 Consultas"])

    with aba_nova:
        pacientes = listar_pacientes()
        if not pacientes:
            st.warning("Cadastre ao menos um paciente antes de agendar uma consulta.")
        else:
            opcoes = {f"{p['nome_completo']} (CPF: {p['cpf']})": p["id"] for p in pacientes}
            with st.form("form_consulta", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                paciente_label = c1.selectbox("Paciente*", list(opcoes.keys()))
                data_consulta = c2.date_input("Data*", value=date.today(), format="DD/MM/YYYY")
                hora_consulta = c3.time_input("Hora*", value=datetime.now().time().replace(second=0, microsecond=0))

                c4, c5 = st.columns(2)
                tipo = c4.selectbox(
                    "Tipo de Consulta", ["Consulta de Rotina", "Retorno", "Exame", "Urgência"]
                )
                medico = c5.text_input("Médico(a) Responsável", placeholder="Dr(a). Nome")
                obs = st.text_area("Observações", placeholder="Alguma observação sobre a consulta")

                if st.form_submit_button("Agendar Consulta", type="primary"):
                    dados = {
                        "paciente_id": opcoes[paciente_label],
                        "data": data_consulta.isoformat(),
                        "hora": hora_consulta.strftime("%H:%M"),
                        "tipo": tipo,
                        "medico": medico.strip(),
                        "observacoes": obs.strip(),
                    }
                    sucesso, msg = inserir_consulta(dados)
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with aba_lista:
        filtro_data = st.date_input(
            "Filtrar por data", value=None, format="DD/MM/YYYY", key="filtro_agenda"
        )
        consultas = listar_consultas(filtro_data.isoformat() if filtro_data else None)

        if not consultas:
            st.info("Nenhuma consulta encontrada.")
        else:
            status_cores = {
                "Agendada": "🟡", "Confirmada": "🟢", "Concluída": "🔵", "Cancelada": "🔴"
            }
            for c in consultas:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    data_fmt = datetime.fromisoformat(c["data"]).strftime("%d/%m/%Y")
                    col1.markdown(f"**{c['nome_completo']}**  \n{c['tipo'] or '—'}")
                    col2.markdown(f"📅 {data_fmt} às {c['hora']}  \n👨‍⚕️ {c['medico'] or '—'}")

                    status_atual = c["status"]
                    novo_status = col3.selectbox(
                        "Status",
                        list(status_cores.keys()),
                        index=list(status_cores.keys()).index(status_atual),
                        key=f"status_{c['id']}",
                        label_visibility="collapsed",
                    )
                    if novo_status != status_atual:
                        atualizar_status_consulta(c["id"], novo_status)
                        st.rerun()

                    if c.get("observacoes"):
                        st.caption(f"📝 {c['observacoes']}")

                    if st.button("🗑️ Cancelar/Excluir", key=f"del_consulta_{c['id']}"):
                        excluir_consulta(c["id"])
                        st.rerun()

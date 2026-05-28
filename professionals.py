import streamlit as st
from database import supabase


def salvar_profissional(
    nome,
    profissao,
    especialidade,
    estado,
    cidade,
    telefone,
    email,
    disponibilidade
):
    dados = {
        "nome": nome,
        "profissao": profissao,
        "especialidade": especialidade,
        "estado": estado,
        "cidade": cidade,
        "telefone": telefone,
        "email": email,
        "disponibilidade": disponibilidade
    }

    supabase.table("profissionais").insert(dados).execute()


def buscar_profissionais():
    response = (
        supabase
        .table("profissionais")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data if response.data else []


def card_profissional(item):
    with st.container(border=True):

        st.markdown(
            f"""
            ### 👨‍⚕️ {item.get("nome", "Profissional")}

            **Profissão:** {item.get("profissao", "-")}

            **Especialidade:** {item.get("especialidade", "-")}

            **Estado:** {item.get("estado", "-")}

            **Cidade:** {item.get("cidade", "-")}

            **Disponibilidade:** {item.get("disponibilidade", "-")}

            **Telefone:** {item.get("telefone", "-")}

            **Email:** {item.get("email", "-")}
            """
        )


def tela_marketplace_profissional():

    st.title("🏥 Marketplace Profissional")

    st.write(
        "Cadastre profissionais da saúde para oportunidades e credenciamentos."
    )

    with st.form("cadastro_profissional"):

        nome = st.text_input("Nome completo")

        profissao = st.selectbox(
            "Profissão",
            [
                "Médico",
                "Enfermeiro",
                "Fisioterapeuta",
                "Psicólogo",
                "Farmacêutico",
                "Biomédico",
                "Técnico de Enfermagem",
                "Dentista",
                "Outro"
            ]
        )

        especialidade = st.text_input(
            "Especialidade"
        )

        estado = st.text_input(
            "Estado"
        )

        cidade = st.text_input(
            "Cidade"
        )

        telefone = st.text_input(
            "Telefone"
        )

        email = st.text_input(
            "Email"
        )

        disponibilidade = st.selectbox(
            "Disponibilidade",
            [
                "Imediata",
                "Parcial",
                "Plantões",
                "CLT",
                "PJ"
            ]
        )

        salvar = st.form_submit_button(
            "💾 Salvar profissional"
        )

        if salvar:

            salvar_profissional(
                nome,
                profissao,
                especialidade,
                estado,
                cidade,
                telefone,
                email,
                disponibilidade
            )

            st.success("Profissional salvo com sucesso!")

    st.divider()

    st.subheader("Profissionais cadastrados")

    profissionais = buscar_profissionais()

    if not profissionais:

        st.warning("Nenhum profissional cadastrado.")

    else:

        for item in profissionais:
            card_profissional(item)
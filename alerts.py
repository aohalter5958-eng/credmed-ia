import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================================
# SALVAR ALERTA
# ==========================================
def salvar_alerta(
    user_email,
    tipo,
    estado,
    palavra_chave,
    frequencia
):

    supabase.table("alerts").insert({
        "user_email": user_email,
        "tipo": tipo,
        "estado": estado,
        "palavra_chave": palavra_chave,
        "frequencia": frequencia
    }).execute()


# ==========================================
# BUSCAR ALERTAS
# ==========================================
def buscar_alertas(user_email):

    response = (
        supabase.table("alerts")
        .select("*")
        .eq("user_email", user_email)
        .order("id", desc=True)
        .execute()
    )

    return response.data


# ==========================================
# TELA ALERTAS
# ==========================================
def tela_alertas(user_email):

    st.markdown("## 🚨 Meus Alertas Inteligentes")

    st.write(
        """
        Configure alertas automáticos para receber novas
        oportunidades de credenciamento e licitação.
        """
    )

    with st.form("novo_alerta"):

        tipo = st.selectbox(
            "Tipo",
            [
                "Credenciamento",
                "Licitação",
                "Todos"
            ]
        )

        estado = st.selectbox(
            "Estado",
            [
                "PR",
                "SP",
                "SC",
                "RS",
                "MG",
                "RJ",
                "Todos"
            ]
        )

        palavra_chave = st.text_input(
            "Palavra-chave",
            placeholder="Ex: médico, hospital, UPA..."
        )

        frequencia = st.selectbox(
            "Frequência",
            [
                "Diário",
                "A cada 12 horas",
                "Semanal"
            ]
        )

        enviar = st.form_submit_button(
            "💾 Salvar alerta"
        )

    if enviar:

        salvar_alerta(
            user_email,
            tipo,
            estado,
            palavra_chave,
            frequencia
        )

        st.success(
            "Alerta salvo com sucesso!"
        )

    st.markdown("---")

    st.markdown("## 📡 Alertas cadastrados")

    alertas = buscar_alertas(user_email)

    if not alertas:

        st.warning(
            "Nenhum alerta cadastrado."
        )

        return

    for alerta in alertas:

        with st.container(border=True):

            st.subheader(
                f"🚨 {alerta['tipo']}"
            )

            st.write(
                f"**Estado:** {alerta['estado']}"
            )

            st.write(
                f"**Palavra-chave:** "
                f"{alerta['palavra_chave']}"
            )

            st.write(
                f"**Frequência:** "
                f"{alerta['frequencia']}"
            )
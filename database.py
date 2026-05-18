from supabase import create_client, Client
import streamlit as st


SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =====================================
# HISTÓRICO
# =====================================

def buscar_historico(user_email):

    response = supabase.table(
        "analyses"
    ).select("*") \
    .eq(
        "user_email",
        user_email
    ) \
    .order(
        "id",
        desc=True
    ) \
    .execute()

    return response.data


# =====================================
# SALVAR ANÁLISE
# =====================================

def salvar_analise(
    nome_arquivo,
    resultado,
    user_email
):

    response = supabase.table(
        "analyses"
    ).insert({

        "nome_arquivo":
            nome_arquivo,

        "resultado":
            resultado,

        "user_email":
            user_email

    }).execute()

    return response
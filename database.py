from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# SALVAR ANÁLISE PDF
# =========================
def salvar_analise(
    nome_arquivo,
    resultado,
    user_email
):
    response = (
        supabase.table("analyses")
        .insert({
            "nome_arquivo": nome_arquivo,
            "resultado": resultado,
            "user_email": user_email
        })
        .execute()
    )

    return response


# =========================
# BUSCAR HISTÓRICO
# =========================
def buscar_historico(user_email):
    response = (
        supabase.table("analyses")
        .select("*")
        .eq("user_email", user_email)
        .order("id", desc=True)
        .execute()
    )

    return response.data


# =========================
# SALVAR OPORTUNIDADE
# =========================
def salvar_oportunidade(dados):
    try:
        numero = dados.get("numero_controle_pncp")

        existente = (
            supabase.table("opportunities")
            .select("id")
            .eq("numero_controle_pncp", numero)
            .execute()
        )

        if existente.data:
            return

        supabase.table("opportunities").insert({
            "numero_controle_pncp": numero,
            "titulo": dados.get("titulo"),
            "tipo": dados.get("tipo"),
            "relevancia": dados.get("relevancia"),
            "score": dados.get("score"),
            "orgao": dados.get("orgao"),
            "local": dados.get("local"),
            "modalidade": dados.get("modalidade"),
            "situacao": dados.get("situacao"),
            "fim_propostas": dados.get("fim_propostas"),
            "valor_estimado": dados.get("valor_estimado"),
            "link": dados.get("link"),
            "fonte": "PNCP"
        }).execute()

    except Exception as erro:
        print("ERRO AO SALVAR OPORTUNIDADE:")
        print(erro)


# =========================
# BUSCAR OPORTUNIDADES
# =========================
def buscar_oportunidades():
    response = (
        supabase.table("opportunities")
        .select("*")
        .order("score", desc=True)
        .limit(200)
        .execute()
    )

    return response.data
import os
import hashlib
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def salvar_analise(nome_arquivo, resultado, user_email):
    return (
        supabase.table("analyses")
        .insert({
            "nome_arquivo": nome_arquivo,
            "resultado": resultado,
            "user_email": user_email
        })
        .execute()
    )


def buscar_historico(user_email):
    response = (
        supabase.table("analyses")
        .select("*")
        .eq("user_email", user_email)
        .order("id", desc=True)
        .execute()
    )
    return response.data


def gerar_hash_oportunidade(item):
    base = (
        str(item.get("numero_controle_pncp", "")) +
        str(item.get("titulo", "")) +
        str(item.get("orgao", "")) +
        str(item.get("local", "")) +
        str(item.get("valor_estimado", ""))
    )
    return hashlib.md5(base.encode("utf-8")).hexdigest()


def salvar_oportunidade(item):
    try:
        hash_unico = gerar_hash_oportunidade(item)

        existente = (
            supabase.table("opportunities")
            .select("id")
            .eq("hash_unico", hash_unico)
            .execute()
        )

        if existente.data:
            return False

        dados = {
            "numero_controle_pncp": item.get("numero_controle_pncp"),
            "titulo": item.get("titulo"),
            "tipo": item.get("tipo"),
            "relevancia": item.get("relevancia"),
            "score": item.get("score"),
            "orgao": item.get("orgao"),
            "local": item.get("local"),
            "modalidade": item.get("modalidade"),
            "situacao": item.get("situacao"),
            "fim_propostas": item.get("fim_propostas"),
            "valor_estimado": str(item.get("valor_estimado")),
            "link": item.get("link"),
            "fonte": "PNCP",
            "hash_unico": hash_unico
        }

        supabase.table("opportunities").insert(dados).execute()
        return True

    except Exception as erro:
        print("Erro ao salvar oportunidade:")
        print(erro)
        return False


def buscar_oportunidades():
    try:
        response = (
            supabase.table("opportunities")
            .select("*")
            .order("score", desc=True)
            .limit(200)
            .execute()
        )
        return response.data

    except Exception as erro:
        print("Erro ao buscar oportunidades:")
        print(erro)
        return []


def salvar_profissional(dados):
    return (
        supabase.table("professionals")
        .insert(dados)
        .execute()
    )


def buscar_profissionais():
    response = (
        supabase.table("professionals")
        .select("*")
        .order("id", desc=True)
        .execute()
    )
    return response.data
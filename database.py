import os
import hashlib
import requests
import streamlit as st

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================================================
# ANÁLISES PDF
# =========================================================

def salvar_analise(nome_arquivo, resultado, user_email):

    return (
        supabase
        .table("analyses")
        .insert({
            "nome_arquivo": nome_arquivo,
            "resultado": resultado,
            "user_email": user_email
        })
        .execute()
    )


def buscar_historico(user_email):

    response = (
        supabase
        .table("analyses")
        .select("*")
        .eq("user_email", user_email)
        .order("id", desc=True)
        .execute()
    )

    return response.data


# =========================================================
# HASH ÚNICO
# =========================================================

def gerar_hash_oportunidade(item):

    base = (
        str(item.get("titulo", "")) +
        str(item.get("orgao", "")) +
        str(item.get("local", "")) +
        str(item.get("valor_estimado", ""))
    )

    return hashlib.md5(base.encode()).hexdigest()


# =========================================================
# SALVAR OPORTUNIDADE
# =========================================================

def salvar_oportunidade(item):

    try:

        hash_unico = gerar_hash_oportunidade(item)

        existente = (
            supabase
            .table("opportunities")
            .select("id")
            .eq("hash_unico", hash_unico)
            .execute()
        )

        if existente.data:
            return False

        dados = {

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


# =========================================================
# BUSCAR OPORTUNIDADES PNCP
# =========================================================

def buscar_oportunidades(paginas=3):

    oportunidades = []

    headers = {
        "accept": "application/json"
    }

    for pagina in range(1, paginas + 1):

        try:

            url = (
                "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"
                "?dataFinal=2099-12-31"
                f"&pagina={pagina}"
                "&tamanhoPagina=50"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            print("STATUS:", response.status_code)

            if response.status_code != 200:
                continue

            dados = response.json()

            lista = dados.get("data", [])

            print("Itens encontrados:", len(lista))

            for item in lista:

                titulo = item.get("objetoCompra", "")

                modalidade = item.get("modalidadeNome", "")

                orgao = (
                    item.get("orgaoEntidade", {})
                    .get("razaoSocial", "")
                )

                municipio = (
                    item.get("unidadeOrgao", {})
                    .get("municipioNome", "")
                )

                uf = (
                    item.get("unidadeOrgao", {})
                    .get("ufSigla", "")
                )

                local = f"{municipio}/{uf}"

                valor = item.get("valorTotalEstimado")

                situacao = item.get("situacaoCompraNome", "")

                data_final = item.get("dataEncerramentoProposta")

                numero_controle = item.get("numeroControlePNCP", "")

                link = (
                    "https://pncp.gov.br/app/editais/"
                    + str(numero_controle)
                )

                texto = (
                    titulo +
                    modalidade +
                    orgao
                ).lower()

                palavras_saude = [

                    "medico",
                    "médico",
                    "enfermagem",
                    "hospital",
                    "ubs",
                    "upa",
                    "saude",
                    "saúde",
                    "farmaceutico",
                    "farmacêutico",
                    "psicologo",
                    "psicólogo",
                    "fisioterapia",
                    "laboratorio",
                    "laboratório",
                    "clinica",
                    "clínica"

                ]

                relevante = any(
                    palavra in texto
                    for palavra in palavras_saude
                )

                if relevante:

                    score = 60

                    oportunidades.append({

                        "titulo": titulo,
                        "tipo": "Credenciamento",
                        "relevancia": "Excelente",
                        "score": score,
                        "orgao": orgao,
                        "local": local,
                        "modalidade": modalidade,
                        "situacao": situacao,
                        "fim_propostas": data_final,
                        "valor_estimado": valor,
                        "link": link

                    })

        except Exception as erro:

            print("Erro ao buscar PNCP:")
            print(erro)

    return oportunidades


# =========================================================
# BASE INTELIGENTE
# =========================================================

def buscar_base_inteligente():

    try:

        response = (
            supabase
            .table("opportunities")
            .select("*")
            .order("id", desc=True)
            .limit(200)
            .execute()
        )

        return response.data

    except Exception as erro:

        print("Erro base inteligente:")
        print(erro)

        return []


# =========================================================
# PROFISSIONAIS
# =========================================================

def salvar_profissional(dados):

    try:

        supabase.table("professionals").insert(dados).execute()

        return True

    except Exception as erro:

        print(erro)

        return False


def buscar_profissionais():

    try:

        response = (
            supabase
            .table("professionals")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        return response.data

    except Exception as erro:

        print(erro)

        return []
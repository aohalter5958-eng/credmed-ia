from supabase import create_client
import os
import requests
from datetime import datetime
import hashlib

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# SALVAR OPORTUNIDADE
# =========================

def salvar_oportunidade(oportunidade):

    try:

        hash_base = (
            str(oportunidade.get("titulo", "")) +
            str(oportunidade.get("orgao", "")) +
            str(oportunidade.get("cidade", ""))
        )

        hash_unico = hashlib.md5(hash_base.encode()).hexdigest()

        oportunidade["hash_unico"] = hash_unico

        existente = (
            supabase
            .table("opportunities")
            .select("id")
            .eq("hash_unico", hash_unico)
            .execute()
        )

        if existente.data:
            return False

        supabase.table("opportunities").insert(oportunidade).execute()

        return True

    except Exception as erro:
        print("Erro ao salvar oportunidade:")
        print(erro)
        return False


# =========================
# BUSCAR OPORTUNIDADES
# =========================

def buscar_oportunidades(paginas=3):

    oportunidades = []

    headers = {
        "accept": "application/json"
    }

    for pagina in range(1, paginas + 1):

        try:

            url = (
                "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
                f"?pagina={pagina}"
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

                orgao = item.get("orgaoEntidade", {}).get("razaoSocial", "")

                cidade = (
                    item.get("unidadeOrgao", {})
                    .get("municipioNome", "")
                )

                uf = (
                    item.get("unidadeOrgao", {})
                    .get("ufSigla", "")
                )

                valor = item.get("valorTotalEstimado")

                data_final = item.get("dataEncerramentoProposta")

                link = (
                    "https://pncp.gov.br/app/editais/"
                    + str(item.get("numeroControlePNCP", ""))
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
                    "psicologo",
                    "fisioterapia",
                    "laboratorio",
                    "clinica"
                ]

                relevante = any(
                    palavra in texto
                    for palavra in palavras_saude
                )

                if relevante:

                    oportunidades.append({

                        "titulo": titulo,
                        "orgao": orgao,
                        "cidade": cidade,
                        "uf": uf,
                        "modalidade": modalidade,
                        "valor": valor,
                        "data_final": data_final,
                        "link": link,
                        "fonte": "PNCP",
                        "created_at": datetime.now().isoformat()

                    })

        except Exception as erro:
            print("Erro PNCP:")
            print(erro)

    return oportunidades


# =========================
# LISTAR BASE INTELIGENTE
# =========================

def listar_oportunidades_salvas():

    try:

        response = (
            supabase
            .table("opportunities")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as erro:
        print(erro)
        return []


# =========================
# SALVAR PROFISSIONAL
# =========================

def salvar_profissional(dados):

    try:

        supabase.table("professionals").insert(dados).execute()

        return True

    except Exception as erro:
        print(erro)
        return False


# =========================
# LISTAR PROFISSIONAIS
# =========================

def listar_profissionais():

    try:

        response = (
            supabase
            .table("professionals")
            .select("*")
            .execute()
        )

        return response.data

    except Exception as erro:
        print(erro)
        return []
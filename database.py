from supabase import create_client
from datetime import datetime
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================
# GERAR HASH ÚNICO
# ==========================================

def gerar_hash_oportunidade(item):

    texto = (
        str(item.get("titulo", "")) +
        str(item.get("orgao", "")) +
        str(item.get("local", "")) +
        str(item.get("valor", ""))
    )

    return hashlib.md5(texto.encode()).hexdigest()


# ==========================================
# SALVAR OPORTUNIDADE
# ==========================================

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
            "orgao": item.get("orgao"),
            "local": item.get("local"),
            "modalidade": item.get("modalidade"),
            "status": item.get("status"),
            "valor": item.get("valor"),
            "data_publicacao": item.get("data_publicacao"),
            "link": item.get("link"),
            "score": item.get("score"),
            "tipo_detectado": item.get("tipo_detectado"),
            "hash_unico": hash_unico,
            "created_at": datetime.now().isoformat()
        }

        (
            supabase
            .table("opportunities")
            .insert(dados)
            .execute()
        )

        return True

    except Exception as e:
        print(f"Erro ao salvar oportunidade: {e}")
        return False


# ==========================================
# BUSCAR OPORTUNIDADES SALVAS
# ==========================================

def buscar_oportunidades():

    try:

        response = (
            supabase
            .table("opportunities")
            .select("*")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )

        return response.data

    except Exception as e:
        print(f"Erro ao buscar oportunidades: {e}")
        return []
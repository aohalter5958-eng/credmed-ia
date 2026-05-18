import os
import json
import requests

from io import BytesIO

import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# ==========================================
# CONFIG
# ==========================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# ==========================================
# AUTH
# ==========================================

def cadastrar_usuario(email, senha):

    url = f"{SUPABASE_URL}/auth/v1/signup"

    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "password": senha
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    return response


def login_usuario(email, senha):

    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "password": senha
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    return response


# ==========================================
# SALVAR ANALISE
# ==========================================

def salvar_analise(nome_arquivo, resultado, user_email):

    url = f"{SUPABASE_URL}/rest/v1/analyses"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    data = {
        "nome_arquivo": nome_arquivo,
        "resultado": resultado,
        "user_email": user_email
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    return response.status_code


# ==========================================
# PDF
# ==========================================

def gerar_pdf(texto):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elementos = []

    linhas = texto.split("\n")

    for linha in linhas:

        elementos.append(
            Paragraph(linha, styles["BodyText"])
        )

        elementos.append(
            Spacer(1, 8)
        )

    doc.build(elementos)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# SESSION
# ==========================================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "email" not in st.session_state:
    st.session_state.email = ""


# ==========================================
# LOGIN SCREEN
# ==========================================

if not st.session_state.logado:

    st.title("🏥 CredMed IA")

    aba1, aba2 = st.tabs(["Login", "Cadastro"])

    # LOGIN
    with aba1:

        st.subheader("Entrar")

        email_login = st.text_input(
            "Email",
            key="login_email"
        )

        senha_login = st.text_input(
            "Senha",
            type="password",
            key="login_senha"
        )

        if st.button("Entrar"):

            resposta = login_usuario(
                email_login,
                senha_login
            )

            if resposta.status_code == 200:

                st.session_state.logado = True
                st.session_state.email = email_login

                st.success("Login realizado!")

                st.rerun()

            else:

                st.error("Email ou senha inválidos")

    # CADASTRO
    with aba2:

        st.subheader("Criar conta")

        email_cadastro = st.text_input(
            "Email ",
            key="cad_email"
        )

        senha_cadastro = st.text_input(
            "Senha ",
            type="password",
            key="cad_senha"
        )

        if st.button("Criar Conta"):

            resposta = cadastrar_usuario(
                email_cadastro,
                senha_cadastro
            )

            if resposta.status_code in [200, 201]:

                st.success(
                    "Conta criada com sucesso!"
                )

            else:

                st.error(
                    "Erro ao criar conta."
                )

    st.stop()


# ==========================================
# APP
# ==========================================

st.sidebar.success(
    f"Logado como: {st.session_state.email}"
)

if st.sidebar.button("Logout"):

    st.session_state.logado = False
    st.session_state.email = ""

    st.rerun()


st.title("🏥 CredMed IA")

st.subheader(
    "Plataforma SaaS de análise de credenciamentos médicos"
)

arquivo = st.file_uploader(
    "Envie um edital PDF",
    type=["pdf"]
)

if arquivo is not None:

    if st.button("🔍 Analisar Edital"):

        with st.spinner("Analisando..."):

            reader = PdfReader(arquivo)

            texto = ""

            for pagina in reader.pages:

                extraido = pagina.extract_text()

                if extraido:
                    texto += extraido + "\n"

            prompt = f"""
Você é especialista em:

- credenciamento médico
- licitações
- saúde pública
- Lei 14.133

Analise o edital abaixo.

Estruture:

1. Resumo
2. Objeto
3. Participantes
4. Documentos
5. Valores
6. Prazos
7. Riscos
8. Próximos passos

EDITAL:
{texto}
"""

            resposta = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            resultado = resposta.output_text

            salvar_analise(
                arquivo.name,
                resultado,
                st.session_state.email
            )

            pdf = gerar_pdf(resultado)

            st.success("Análise concluída!")

            st.markdown(resultado)

            c1, c2 = st.columns(2)

            with c1:

                st.download_button(
                    label="📥 TXT",
                    data=resultado,
                    file_name="relatorio.txt",
                    mime="text/plain"
                )

            with c2:

                st.download_button(
                    label="📄 PDF",
                    data=pdf,
                    file_name="relatorio.pdf",
                    mime="application/pdf"
                )
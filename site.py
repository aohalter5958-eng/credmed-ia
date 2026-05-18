import os
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
from supabase import create_client, Client

# =====================================
# CONFIG
# =====================================

st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)

load_dotenv()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =====================================
# CSS
# =====================================

st.markdown("""
<style>

.main {
    background: #0b1020;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: white;
}

[data-testid="stSidebar"] {
    background: #111827;
}

.stButton>button {
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 18px;
    font-weight: bold;
}

.stButton>button:hover {
    opacity: 0.9;
}

.card {
    background: #111827;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOGIN / CADASTRO
# =====================================

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:

    st.title("🏥 CredMed IA")

    tab1, tab2 = st.tabs([
        "Login",
        "Cadastro"
    ])

    # LOGIN
    with tab1:

        st.subheader("Entrar")

        login_email = st.text_input(
            "E-mail",
            key="login_email"
        )

        login_password = st.text_input(
            "Senha",
            type="password",
            key="login_password"
        )

        if st.button("Entrar"):

            try:

                response = supabase.auth.sign_in_with_password({
                    "email": login_email,
                    "password": login_password
                })

                st.session_state.user = response.user.email
                st.rerun()

            except:
                st.error("Email ou senha inválidos")

    # CADASTRO
    with tab2:

        st.subheader("Criar conta")

        signup_email = st.text_input(
            "E-mail",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Senha",
            type="password",
            key="signup_password"
        )

        if st.button("Criar Conta"):

            try:

                supabase.auth.sign_up({
                    "email": signup_email,
                    "password": signup_password
                })

                st.success(
                    "Conta criada com sucesso!"
                )

            except Exception as e:
                st.error(str(e))

    st.stop()

# =====================================
# USUÁRIO LOGADO
# =====================================

user_email = st.session_state.user

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.success(f"Logado como:\n\n{user_email}")

    if st.button("Logout"):

        st.session_state.user = None
        st.rerun()

    st.markdown("---")

    st.markdown("## 📂 Histórico")

    try:

        historico = supabase.table("analyses") \
            .select("*") \
            .eq("user_email", user_email) \
            .order("id", desc=True) \
            .execute()

        if historico.data:

            for item in historico.data:

                with st.expander(
                    f"📄 {item['nome_arquivo'][:25]}"
                ):

                    st.caption(item["criado_em"])

                    if st.button(
                        f"Abrir análise {item['id']}",
                        key=f"abrir_{item['id']}"
                    ):

                        st.session_state[
                            "resultado_antigo"
                        ] = item["resultado"]

        else:

            st.info(
                "Nenhuma análise encontrada."
            )

    except:
        st.error("Erro ao carregar histórico")

# =====================================
# HEADER
# =====================================

st.markdown("""
<div class="card">

<h1>🏥 CredMed IA</h1>

<h3>
Plataforma SaaS de análise de
credenciamentos médicos
</h3>

</div>
""", unsafe_allow_html=True)

# =====================================
# UPLOAD
# =====================================

uploaded_file = st.file_uploader(
    "Envie um edital PDF",
    type=["pdf"]
)

# =====================================
# PROCESSAMENTO
# =====================================

if uploaded_file is not None:

    if st.button("🔍 Analisar Edital"):

        with st.spinner("Analisando edital..."):

            pdf = PdfReader(uploaded_file)

            texto = ""

            for page in pdf.pages:

                try:
                    texto += page.extract_text()
                except:
                    pass

            prompt = f"""
            Analise este edital médico.

            Gere:

            1. Resumo executivo
            2. Documentos exigidos
            3. Prazos importantes
            4. Valores e pagamentos
            5. Riscos do edital
            6. Próximos passos

            EDITAL:
            {texto[:15000]}
            """

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            resultado = response.output_text

            # =====================================
            # SALVAR SUPABASE
            # =====================================

            try:

                supabase.table("analyses").insert({

                    "nome_arquivo":
                        uploaded_file.name,

                    "resultado":
                        resultado,

                    "user_email":
                        user_email

                }).execute()

            except Exception as e:

                st.error(
                    f"Erro ao salvar: {e}"
                )

            # =====================================
            # RESULTADO
            # =====================================

            st.success("Análise concluída!")

            st.markdown(resultado)

            # =====================================
            # PDF
            # =====================================

            buffer = BytesIO()

            doc = SimpleDocTemplate(buffer)

            styles = getSampleStyleSheet()

            story = []

            story.append(
                Paragraph(
                    "Relatório CredMed IA",
                    styles["Title"]
                )
            )

            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    resultado.replace("\n", "<br/>"),
                    styles["BodyText"]
                )
            )

            doc.build(story)

            pdf_bytes = buffer.getvalue()

            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_bytes,
                file_name="relatorio.pdf",
                mime="application/pdf"
            )

# =====================================
# ANÁLISE ANTIGA
# =====================================

if "resultado_antigo" in st.session_state:

    st.markdown("---")

    st.subheader("📂 Análise salva")

    st.markdown(
        st.session_state[
            "resultado_antigo"
        ]
    )
import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from supabase import create_client, Client

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
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("""
<style>
.stApp {
    background: #050816;
    color: white;
}

html, body, p, label, span, div, h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1300px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1020, #111827);
    border-right: 1px solid #1f2937;
}

.stTextInput input {
    background: #111827 !important;
    color: white !important;
    border-radius: 12px;
}

.card {
    background: linear-gradient(180deg, #111827, #0f172a);
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 28px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

.metric-card {
    background: linear-gradient(180deg, #111827, #0b1020);
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
}

.metric-title {
    color: #9ca3af !important;
    font-size: 14px;
}

.metric-value {
    color: white !important;
    font-size: 32px;
    font-weight: 800;
}

.hero {
    background:
        radial-gradient(circle at top left, rgba(124,58,237,0.4), transparent 40%),
        linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #1f2937;
    border-radius: 25px;
    padding: 45px;
    margin-bottom: 30px;
}

.result-box {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 25px;
    color: white;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #16a34a, #15803d) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

def gerar_pdf(texto):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Relatório CredMed IA", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(texto.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

if "user" not in st.session_state:
    st.session_state.user = None

if "resultado_antigo" not in st.session_state:
    st.session_state.resultado_antigo = None

if st.session_state.user is None:

    st.markdown("""
    <div class="hero">
        <h1>🏥 CredMed IA</h1>
        <h3>Plataforma SaaS premium para análise inteligente de credenciamentos médicos e editais públicos.</h3>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Cadastro"])

    with tab1:
        st.subheader("Entrar")

        login_email = st.text_input("E-mail", key="login_email")
        login_password = st.text_input("Senha", type="password", key="login_password")

        if st.button("Entrar"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": login_email,
                    "password": login_password
                })

                st.session_state.user = response.user.email
                st.rerun()

            except Exception:
                st.error("Email ou senha inválidos")

    with tab2:
        st.subheader("Criar conta")

        signup_email = st.text_input("E-mail", key="signup_email")
        signup_password = st.text_input("Senha", type="password", key="signup_password")

        if st.button("Criar Conta"):
            try:
                supabase.auth.sign_up({
                    "email": signup_email,
                    "password": signup_password
                })

                st.success("Conta criada com sucesso!")

            except Exception as e:
                st.error(str(e))

    st.stop()

user_email = st.session_state.user

historico = supabase.table("analyses") \
    .select("*") \
    .eq("user_email", user_email) \
    .order("id", desc=True) \
    .execute()

analyses = historico.data

with st.sidebar:
    st.markdown("## 🏥 CredMed IA")

    st.success(f"Logado como:\n\n{user_email}")

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.resultado_antigo = None
        st.rerun()

    st.markdown("---")
    st.markdown("## 📂 Histórico")

    if analyses:
        for item in analyses:
            with st.expander(f"📄 {item['nome_arquivo'][:28]}"):
                st.caption(item["criado_em"])

                if st.button(f"Abrir {item['id']}", key=f"abrir_{item['id']}"):
                    st.session_state.resultado_antigo = item["resultado"]
                    st.rerun()
    else:
        st.info("Nenhuma análise encontrada.")

st.markdown("""
<div class="hero">
    <h1>🏥 CredMed IA</h1>
    <h3>Plataforma SaaS de análise inteligente de credenciamentos médicos, editais hospitalares e chamadas públicas.</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total de análises</div>
        <div class="metric-value">{len(analyses)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Plano</div>
        <div class="metric-value">FREE</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Status</div>
        <div class="metric-value">ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Exportação</div>
        <div class="metric-value">PDF</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h2>📄 Nova análise</h2>
    <p>Envie um edital PDF e receba uma análise estruturada com IA.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Envie um edital PDF", type=["pdf"])

if uploaded_file is not None:

    if st.button("🔍 Analisar Edital"):

        with st.spinner("Analisando edital..."):

            pdf_reader = PdfReader(uploaded_file)
            texto = ""

            for page in pdf_reader.pages:
                try:
                    texto_extraido = page.extract_text()
                    if texto_extraido:
                        texto += texto_extraido + "\n"
                except Exception:
                    pass

            prompt = f"""
Você é especialista em credenciamento médico, licitações, saúde pública e Lei 14.133.

Analise este edital médico e gere uma resposta profissional contendo:

1. Resumo executivo
2. Órgão responsável
3. Objeto do credenciamento
4. Quem pode participar
5. Documentos exigidos
6. Prazos importantes
7. Valores e pagamentos
8. Riscos do edital
9. Impedimentos
10. Próximos passos recomendados
11. Conclusão

Use linguagem clara, objetiva e prática.

EDITAL:
{texto[:15000]}
"""

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            resultado = response.output_text

            supabase.table("analyses").insert({
                "nome_arquivo": uploaded_file.name,
                "resultado": resultado,
                "user_email": user_email
            }).execute()

            pdf_bytes = gerar_pdf(resultado)

            st.success("Análise concluída!")

            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(resultado)
            st.markdown('</div>', unsafe_allow_html=True)

            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_bytes,
                file_name="relatorio_credmed_ia.pdf",
                mime="application/pdf"
            )

if st.session_state.resultado_antigo:

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h2>📂 Análise salva</h2>
    </div>
    """, unsafe_allow_html=True)

    pdf_antigo = gerar_pdf(st.session_state.resultado_antigo)

    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(st.session_state.resultado_antigo)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button(
        label="📄 Baixar PDF da análise salva",
        data=pdf_antigo,
        file_name="analise_salva_credmed_ia.pdf",
        mime="application/pdf"
    )
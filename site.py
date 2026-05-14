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


# =========================
# CONFIG
# =========================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# =========================
# SALVAR ANALISE
# =========================

def salvar_analise(nome_arquivo, resultado):

    url = f"{SUPABASE_URL}/rest/v1/analyses"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    data = {
        "nome_arquivo": nome_arquivo,
        "resultado": resultado
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    return response.status_code


# =========================
# PDF
# =========================

def gerar_pdf(texto):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    titulo_style = styles["Title"]
    titulo_style.fontSize = 22
    titulo_style.spaceAfter = 20

    subtitulo_style = styles["Heading2"]
    subtitulo_style.fontSize = 14
    subtitulo_style.spaceAfter = 16

    texto_style = styles["BodyText"]
    texto_style.fontSize = 10
    texto_style.leading = 14
    texto_style.spaceAfter = 10

    elementos = []

    elementos.append(
        Paragraph("<b>CredMed IA</b>", titulo_style)
    )

    elementos.append(
        Paragraph(
            "Relatório Profissional de Análise de Credenciamento Médico",
            subtitulo_style
        )
    )

    elementos.append(
        Paragraph(
            "Documento gerado automaticamente pela plataforma CredMed IA.",
            texto_style
        )
    )

    elementos.append(Spacer(1, 20))

    linhas = texto.split("\n")

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            elementos.append(Spacer(1, 8))
            continue

        if linha.startswith("# "):

            elementos.append(
                Paragraph(
                    f"<b>{linha.replace('# ', '')}</b>",
                    styles["Heading1"]
                )
            )

        elif linha.startswith("## "):

            elementos.append(
                Paragraph(
                    f"<b>{linha.replace('## ', '')}</b>",
                    styles["Heading2"]
                )
            )

        elif linha.startswith("- "):

            elementos.append(
                Paragraph(
                    f"• {linha.replace('- ', '')}",
                    texto_style
                )
            )

        else:

            elementos.append(
                Paragraph(
                    linha,
                    texto_style
                )
            )

    elementos.append(Spacer(1, 20))

    elementos.append(
        Paragraph(
            "<i>CredMed IA • Plataforma SaaS de análise de credenciamentos médicos.</i>",
            texto_style
        )
    )

    doc.build(elementos)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


# =========================
# PAGE
# =========================

st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)


# =========================
# CSS
# =========================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background:
    radial-gradient(circle at top left, #1e3a8a 0%, transparent 30%),
    radial-gradient(circle at bottom right, #0f172a 0%, transparent 30%),
    linear-gradient(135deg, #020617 0%, #0f172a 50%, #111827 100%);
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero {
    background: linear-gradient(
        135deg,
        rgba(30,41,59,0.95),
        rgba(15,23,42,0.92)
    );

    border: 1px solid rgba(148,163,184,0.15);

    border-radius: 32px;

    padding: 48px;

    margin-bottom: 30px;

    box-shadow:
    0 25px 80px rgba(0,0,0,0.45);
}

.badge {
    display: inline-block;

    background: rgba(34,197,94,0.12);

    color: #86efac;

    border: 1px solid rgba(34,197,94,0.28);

    padding: 10px 18px;

    border-radius: 999px;

    font-size: 13px;

    font-weight: 800;

    margin-bottom: 20px;
}

.logo {
    font-size: 62px;
    font-weight: 900;
    color: white;
    letter-spacing: -3px;
}

.subtitle {
    color: #cbd5e1;
    font-size: 25px;
    margin-top: 12px;
    max-width: 950px;
    line-height: 1.5;
}

.card {
    background: rgba(255,255,255,0.97);

    border-radius: 28px;

    padding: 30px;

    box-shadow:
    0 25px 60px rgba(0,0,0,0.30);

    border: 1px solid rgba(255,255,255,0.12);

    margin-bottom: 22px;
}

.card-dark {

    background: rgba(15,23,42,0.88);

    border-radius: 28px;

    padding: 34px;

    box-shadow:
    0 25px 60px rgba(0,0,0,0.35);

    border: 1px solid rgba(148,163,184,0.15);

    color: white;
}

.metric-title {
    color: #64748b;
    font-size: 14px;
    font-weight: 800;
    text-transform: uppercase;
}

.metric-number {
    color: #0f172a;
    font-size: 34px;
    font-weight: 900;
}

.upload-title {
    color: #0f172a;
    font-size: 28px;
    font-weight: 900;
    margin-bottom: 10px;
}

.upload-desc {
    color: #475569;
    font-size: 17px;
    line-height: 1.7;
}

.feature {

    background: rgba(255,255,255,0.06);

    border-radius: 18px;

    padding: 16px;

    margin-bottom: 14px;

    border: 1px solid rgba(148,163,184,0.12);
}

.feature strong {
    color: white;
}

.feature span {
    color: #cbd5e1;
}

.result-box {

    background: white;

    border-radius: 28px;

    padding: 38px;

    margin-top: 25px;

    box-shadow:
    0 25px 70px rgba(0,0,0,0.35);
}

.footer {

    color: #94a3b8;

    text-align: center;

    margin-top: 40px;

    font-size: 14px;
}

.stButton button {

    background:
    linear-gradient(135deg, #0284c7, #2563eb) !important;

    color: white !important;

    border: none !important;

    border-radius: 16px !important;

    height: 58px !important;

    font-size: 18px !important;

    font-weight: 900 !important;

    width: 100% !important;

    box-shadow:
    0 18px 36px rgba(37,99,235,0.35);
}

.stDownloadButton button {

    background:
    linear-gradient(135deg, #16a34a, #15803d) !important;

    color: white !important;

    border: none !important;

    border-radius: 16px !important;

    height: 54px !important;

    font-size: 16px !important;

    font-weight: 900 !important;

    width: 100% !important;
}

</style>
""", unsafe_allow_html=True)


# =========================
# HERO
# =========================

st.markdown("""
<div class="hero">

<div class="badge">
MVP ONLINE • IA PARA SAÚDE PÚBLICA
</div>

<div class="logo">
🏥 CredMed IA
</div>

<div class="subtitle">
Plataforma inteligente para análise de editais,
chamamentos públicos e credenciamentos médicos.
</div>

</div>
""", unsafe_allow_html=True)


# =========================
# METRICS
# =========================

m1, m2, m3 = st.columns(3)

with m1:

    st.markdown("""
    <div class="card">

    <div class="metric-title">
    ANÁLISE
    </div>

    <div class="metric-number">
    PDF
    </div>

    <p>Leitura automática de editais médicos.</p>

    </div>
    """, unsafe_allow_html=True)

with m2:

    st.markdown("""
    <div class="card">

    <div class="metric-title">
    ENTREGA
    </div>

    <div class="metric-number">
    Relatório
    </div>

    <p>Resumo, riscos, prazos e documentos.</p>

    </div>
    """, unsafe_allow_html=True)

with m3:

    st.markdown("""
    <div class="card">

    <div class="metric-title">
    EXPORTAÇÃO
    </div>

    <div class="metric-number">
    PDF/TXT
    </div>

    <p>Baixe o resultado para salvar ou enviar.</p>

    </div>
    """, unsafe_allow_html=True)


# =========================
# MAIN
# =========================

col1, col2 = st.columns([1.4, 1])

with col1:

    st.markdown("""
    <div class="card">

    <div class="upload-title">
    Enviar edital para análise
    </div>

    <div class="upload-desc">
    Faça upload de um edital em PDF.
    A IA irá identificar:
    requisitos,
    documentos,
    riscos,
    prazos,
    pagamentos,
    impedimentos
    e próximos passos recomendados.
    </div>
    """, unsafe_allow_html=True)

    arquivo = st.file_uploader(
        "Selecione o edital em PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="card-dark">

    <h1>O que o sistema analisa?</h1>

    <div class="feature">
    <strong>✅ Documentos exigidos</strong><br>
    <span>Empresa, médicos, RT e certidões.</span>
    </div>

    <div class="feature">
    <strong>✅ Prazos importantes</strong><br>
    <span>Datas, vigência e recursos.</span>
    </div>

    <div class="feature">
    <strong>✅ Valores e pagamentos</strong><br>
    <span>Plantões, consultas e pagamentos.</span>
    </div>

    <div class="feature">
    <strong>✅ Riscos do edital</strong><br>
    <span>Exigências que podem impedir participação.</span>
    </div>

    <div class="feature">
    <strong>✅ Próximos passos</strong><br>
    <span>Checklist prático para preparação.</span>
    </div>

    </div>
    """, unsafe_allow_html=True)


# =========================
# ANALISE
# =========================

if arquivo is not None:

    st.info(f"Arquivo carregado: {arquivo.name}")

    if st.button("🔍 Analisar Edital Agora"):

        with st.spinner("Analisando edital..."):

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
- análise documental
- contratos públicos

Analise o edital abaixo.

Estruture exatamente assim:

# 1. Resumo Executivo

# 2. Órgão Responsável

# 3. Objeto

# 4. Quem Pode Participar

# 5. Serviços Aceitos

# 6. Valores

# 7. Prazos

# 8. Checklist de Documentos

# 9. Riscos

# 10. Impedimentos

# 11. Próximos Passos

# 12. Conclusão

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
                resultado
            )

            pdf = gerar_pdf(resultado)

            st.success("✅ Análise concluída!")

            st.markdown(
                '<div class="result-box">',
                unsafe_allow_html=True
            )

            st.markdown("## 📋 Resultado da Análise")

            st.markdown(resultado)

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            d1, d2 = st.columns(2)

            with d1:

                st.download_button(
                    label="📥 Baixar TXT",
                    data=resultado,
                    file_name="relatorio.txt",
                    mime="text/plain"
                )

            with d2:

                st.download_button(
                    label="📄 Baixar PDF",
                    data=pdf,
                    file_name="relatorio_credmed_ia.pdf",
                    mime="application/pdf"
                )


# =========================
# FOOTER
# =========================

st.markdown("""
<div class="footer">
CredMed IA • Plataforma SaaS de análise de credenciamentos médicos públicos
</div>
""", unsafe_allow_html=True)
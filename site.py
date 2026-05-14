import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


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
                Paragraph(f"<b>{linha.replace('# ', '')}</b>", styles["Heading1"])
            )

        elif linha.startswith("## "):
            elementos.append(
                Paragraph(f"<b>{linha.replace('## ', '')}</b>", styles["Heading2"])
            )

        elif linha.startswith("- "):
            elementos.append(
                Paragraph(f"• {linha.replace('- ', '')}", texto_style)
            )

        else:
            elementos.append(
                Paragraph(linha, texto_style)
            )

    elementos.append(Spacer(1, 20))

    elementos.append(
        Paragraph(
            "<i>CredMed IA • Análise inteligente de editais e credenciamentos médicos públicos.</i>",
            texto_style
        )
    )

    doc.build(elementos)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)


st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #1e293b 100%);
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(37,99,235,0.10));
    border: 1px solid rgba(148,163,184,0.22);
    border-radius: 30px;
    padding: 42px;
    margin-bottom: 30px;
    box-shadow: 0 25px 80px rgba(0,0,0,0.35);
}

.badge {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.35);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 20px;
}

.logo {
    font-size: 52px;
    font-weight: 900;
    color: white;
    letter-spacing: -2px;
}

.subtitle {
    color: #cbd5e1;
    font-size: 23px;
    margin-top: 10px;
    max-width: 900px;
}

.card {
    background: rgba(255,255,255,0.96);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    margin-bottom: 20px;
    border: 1px solid rgba(226,232,240,0.9);
}

.card-dark {
    background: rgba(15,23,42,0.86);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    border: 1px solid rgba(148,163,184,0.18);
    color: white;
}

.metric-title {
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
}

.metric-number {
    color: #0f172a;
    font-size: 30px;
    font-weight: 900;
}

.feature {
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(148,163,184,0.16);
}

.feature strong {
    color: white;
}

.feature span {
    color: #cbd5e1;
}

.upload-title {
    color: #0f172a;
    font-size: 24px;
    font-weight: 900;
    margin-bottom: 10px;
}

.upload-desc {
    color: #475569;
    font-size: 16px;
    line-height: 1.6;
}

.result-box {
    background: white;
    border-radius: 24px;
    padding: 34px;
    margin-top: 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}

.result-box h1,
.result-box h2,
.result-box h3 {
    color: #0f172a !important;
}

.footer {
    color: #94a3b8;
    text-align: center;
    margin-top: 35px;
    font-size: 14px;
}

.stButton button {
    background: linear-gradient(135deg, #0284c7, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    height: 56px !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    width: 100% !important;
    box-shadow: 0 16px 32px rgba(37,99,235,0.28);
}

.stDownloadButton button {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    height: 52px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    width: 100% !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
<div class="badge">MVP ONLINE • IA PARA SAÚDE PÚBLICA</div>
<div class="logo">🏥 CredMed IA</div>
<div class="subtitle">
Plataforma inteligente para análise de editais,
chamamentos públicos e credenciamentos médicos.
</div>
</div>
""", unsafe_allow_html=True)


m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="card">
    <div class="metric-title">ANÁLISE</div>
    <div class="metric-number">PDF</div>
    <p>Leitura automática de editais médicos.</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="card">
    <div class="metric-title">ENTREGA</div>
    <div class="metric-number">Relatório</div>
    <p>Resumo, riscos, prazos e documentos.</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="card">
    <div class="metric-title">EXPORTAÇÃO</div>
    <div class="metric-number">PDF/TXT</div>
    <p>Baixe o resultado para salvar ou enviar.</p>
    </div>
    """, unsafe_allow_html=True)


col1, col2 = st.columns([1.4, 1])

with col1:

    st.markdown("""
    <div class="card">
    <div class="upload-title">Enviar edital para análise</div>
    <div class="upload-desc">
    Faça upload de um edital em PDF.
    A IA irá identificar o objeto, requisitos,
    prazos, documentos exigidos, valores,
    riscos e próximos passos recomendados.
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
    <h2>O que o sistema analisa?</h2>

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
    <span>Plantões, consultas e formas de pagamento.</span>
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


if arquivo is not None:

    st.info(f"Arquivo carregado: {arquivo.name}")

    if st.button("🔍 Analisar Edital Agora"):

        with st.spinner("Analisando edital..."):

            reader = PdfReader(arquivo)

            texto = ""

            for pagina in reader.pages:

                texto_extraido = pagina.extract_text()

                if texto_extraido:
                    texto += texto_extraido + "\n"

            prompt = f"""
Você é uma IA especialista em:

- credenciamentos médicos públicos
- chamamentos públicos
- licitações
- Lei 14.133/2021
- contratação de serviços de saúde
- análise documental para empresas médicas

Analise o edital abaixo e gere um RELATÓRIO PROFISSIONAL.

Estruture exatamente assim:

# 1. Resumo Executivo

# 2. Órgão Responsável

# 3. Objeto do Credenciamento

# 4. Quem Pode Participar

# 5. Especialidades e Serviços Aceitos

# 6. Valores e Forma de Pagamento

# 7. Prazos Importantes

# 8. Checklist de Documentos

# 9. Exigências que Podem Impedir Participação

# 10. Pontos de Atenção e Riscos

# 11. Informações Não Localizadas

# 12. Próximos Passos Recomendados

Regras:
- Use linguagem simples.
- Não invente informações.

EDITAL:
{texto}
"""

            resposta = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            resultado = resposta.output_text

            pdf = gerar_pdf(resultado)

            st.success("✅ Análise concluída com sucesso!")

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
                    label="📥 Baixar relatório em TXT",
                    data=resultado,
                    file_name="relatorio_credmed_ia.txt",
                    mime="text/plain"
                )

            with d2:

                st.download_button(
                    label="📄 Baixar relatório em PDF",
                    data=pdf,
                    file_name="relatorio_credmed_ia.pdf",
                    mime="application/pdf"
                )


st.markdown("""
<div class="footer">
CredMed IA • Análise inteligente de editais e credenciamentos médicos públicos
</div>
""", unsafe_allow_html=True)
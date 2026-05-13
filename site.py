import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# =========================
# CONFIGURAÇÃO OPENAI
# =========================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# =========================
# FUNÇÃO PDF
# =========================

def gerar_pdf(texto):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elementos = []

    titulo = Paragraph(
        "<b>Relatório CredMed IA</b>",
        styles['Title']
    )

    elementos.append(titulo)

    elementos.append(Spacer(1, 20))

    texto_formatado = texto.replace("\n", "<br/>")

    paragrafo = Paragraph(
        texto_formatado,
        styles['BodyText']
    )

    elementos.append(paragrafo)

    doc.build(elementos)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

# =========================
# CONFIGURAÇÃO DA PÁGINA
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

.main {
    background-color: #f8fafc;
}

.titulo {
    font-size: 42px;
    font-weight: 800;
    color: #0f172a;
}

.subtitulo {
    font-size: 22px;
    color: #334155;
    margin-bottom: 25px;
}

.card {
    background-color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.destaque {
    background-color: #e0f2fe;
    padding: 18px;
    border-left: 6px solid #0284c7;
    border-radius: 12px;
    margin-bottom: 25px;
}

.stButton button {
    background-color: #0284c7;
    color: white;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
    font-weight: 600;
    width: 100%;
}

.stDownloadButton button {
    background-color: #16a34a;
    color: white;
    border-radius: 12px;
    height: 50px;
    font-size: 17px;
    font-weight: 600;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================

st.markdown(
    '<div class="titulo">🏥 CredMed IA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Análise Inteligente de Credenciamentos Médicos</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="destaque">
Envie um edital médico em PDF e receba automaticamente um relatório com:
resumo, documentos exigidos, prazos, valores, riscos e próximos passos.
</div>
""", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================

col1, col2 = st.columns([2, 1])

with col1:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    arquivo = st.file_uploader(
        "📄 Selecione o edital em PDF",
        type=["pdf"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="card">
    <h3>O que a IA analisa?</h3>

    <p>✅ Documentos exigidos</p>
    <p>✅ Prazos importantes</p>
    <p>✅ Valores e pagamentos</p>
    <p>✅ Riscos do edital</p>
    <p>✅ Próximos passos</p>

    </div>
    """, unsafe_allow_html=True)

# =========================
# PROCESSAMENTO
# =========================

if arquivo is not None:

    if st.button("🔍 Analisar Edital"):

        with st.spinner("Analisando edital... aguarde alguns segundos."):

            # LER PDF
            reader = PdfReader(arquivo)

            texto = ""

            for pagina in reader.pages:

                texto_extraido = pagina.extract_text()

                if texto_extraido:

                    texto += texto_extraido + "\n"

            # PROMPT IA
            prompt = f"""
Você é uma IA especialista em:

- credenciamentos médicos públicos
- licitações
- Lei 14.133/2021
- contratação de serviços de saúde

Analise o edital abaixo e gere um RELATÓRIO PROFISSIONAL.

Sua resposta deve conter:

# 1. Resumo Executivo

# 2. Órgão Responsável

# 3. Objeto do Credenciamento

# 4. Quem Pode Participar

# 5. Especialidades e Serviços Aceitos

# 6. Valores e Forma de Pagamento

# 7. Prazos Importantes

# 8. Checklist de Documentos

# 9. Riscos e Pontos de Atenção

# 10. Próximos Passos Recomendados

Regras:
- Use linguagem simples.
- Não invente informações.

EDITAL:
{texto}
"""

            # IA
            resposta = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            resultado = resposta.output_text

            # RESULTADO
            st.success("✅ Análise concluída!")

            st.markdown("## 📋 Resultado da Análise")

            st.markdown(resultado)

            # DOWNLOAD TXT
            st.download_button(
                label="📥 Baixar relatório em TXT",
                data=resultado,
                file_name="relatorio_credmed_ia.txt",
                mime="text/plain"
            )

            # GERAR PDF
            pdf = gerar_pdf(resultado)

            # DOWNLOAD PDF
            st.download_button(
                label="📄 Baixar relatório em PDF",
                data=pdf,
                file_name="relatorio_credmed_ia.pdf",
                mime="application/pdf"
            )
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
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("<b>Relatório CredMed IA</b>", styles["Title"]))
    elementos.append(Spacer(1, 20))

    texto_formatado = texto.replace("\n", "<br/>")
    elementos.append(Paragraph(texto_formatado, styles["BodyText"]))

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
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

.hero {
    background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(37,99,235,0.10));
    border: 1px solid rgba(148,163,184,0.22);
    border-radius: 28px;
    padding: 38px;
    box-shadow: 0 25px 80px rgba(0,0,0,0.35);
    margin-bottom: 28px;
}

.logo {
    font-size: 48px;
    font-weight: 900;
    color: #f8fafc;
    letter-spacing: -1.5px;
}

.subtitle {
    color: #cbd5e1;
    font-size: 22px;
    margin-top: 8px;
}

.badge {
    display: inline-block;
    background: rgba(34,197,94,0.16);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.35);
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 18px;
}

.card {
    background: rgba(255,255,255,0.96);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.25);
    border: 1px solid rgba(226,232,240,0.9);
    margin-bottom: 20px;
}

.card-dark {
    background: rgba(15,23,42,0.86);
    border-radius: 24px;
    padding: 28px;
    border: 1px solid rgba(148,163,184,0.22);
    box-shadow: 0 25px 70px rgba(0,0,0,0.25);
    color: #e2e8f0;
}

.metric-title {
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
}

.metric-number {
    color: #0f172a;
    font-size: 28px;
    font-weight: 900;
}

.feature {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(148,163,184,0.18);
}

.feature strong {
    color: #f8fafc;
}

.feature span {
    color: #cbd5e1;
}

.stButton button {
    background: linear-gradient(135deg, #0284c7, #2563eb);
    color: white;
    border-radius: 14px;
    height: 56px;
    font-size: 18px;
    font-weight: 800;
    width: 100%;
    border: none;
    box-shadow: 0 16px 32px rgba(37,99,235,0.28);
}

.stButton button:hover {
    background: linear-gradient(135deg, #0369a1, #1d4ed8);
    color: white;
}

.stDownloadButton button {
    background: linear-gradient(135deg, #16a34a, #15803d);
    color: white;
    border-radius: 14px;
    height: 52px;
    font-size: 16px;
    font-weight: 800;
    width: 100%;
    border: none;
}

h1, h2, h3 {
    color: #f8fafc;
}

.upload-title {
    color: #0f172a;
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 8px;
}

.upload-desc {
    color: #475569;
    font-size: 15px;
    margin-bottom: 18px;
}

.result-box {
    background: white;
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    margin-top: 24px;
}

.result-box h1, .result-box h2, .result-box h3 {
    color: #0f172a !important;
}

.footer {
    color: #94a3b8;
    text-align: center;
    margin-top: 32px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <div class="badge">MVP ONLINE • IA PARA SAÚDE PÚBLICA</div>
    <div class="logo">🏥 CredMed IA</div>
    <div class="subtitle">
        Plataforma inteligente para análise de editais, chamamentos públicos e credenciamentos médicos.
    </div>
</div>
""", unsafe_allow_html=True)


m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="card">
        <div class="metric-title">Análise</div>
        <div class="metric-number">PDF</div>
        <p>Leitura automática de editais médicos.</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="card">
        <div class="metric-title">Entrega</div>
        <div class="metric-number">Relatório</div>
        <p>Resumo, riscos, prazos e documentos.</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="card">
        <div class="metric-title">Exportação</div>
        <div class="metric-number">PDF/TXT</div>
        <p>Baixe o resultado para salvar ou enviar.</p>
    </div>
    """, unsafe_allow_html=True)


col1, col2 = st.columns([1.35, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="upload-title">Enviar edital para análise</div>
        <div class="upload-desc">
            Faça upload de um edital em PDF. A IA irá identificar o objeto, requisitos, prazos,
            documentos exigidos, valores, riscos e próximos passos recomendados.
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
        <h3>O que o sistema analisa?</h3>

        <div class="feature"><strong>✅ Documentos exigidos</strong><br><span>Empresa, médicos, RT e certidões.</span></div>
        <div class="feature"><strong>✅ Prazos e vigência</strong><br><span>Datas, sessões, recursos e validade.</span></div>
        <div class="feature"><strong>✅ Valores e pagamento</strong><br><span>Plantões, consultas, hora médica e forma de pagamento.</span></div>
        <div class="feature"><strong>✅ Riscos do edital</strong><br><span>Exigências que podem impedir participação.</span></div>
        <div class="feature"><strong>✅ Próximos passos</strong><br><span>Checklist prático para a empresa se preparar.</span></div>
    </div>
    """, unsafe_allow_html=True)


if arquivo is not None:
    st.markdown("### Pronto para analisar")
    st.info(f"Arquivo carregado: {arquivo.name}")

    if st.button("🔍 Analisar Edital Agora"):

        with st.spinner("Analisando edital... isso pode levar alguns segundos."):

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

Analise o edital abaixo e gere um RELATÓRIO PROFISSIONAL para uma empresa médica interessada em participar.

A resposta deve ser clara, comercial, prática e objetiva.

Estruture exatamente assim:

# 1. Resumo Executivo
Explique em linguagem simples do que trata o edital.

# 2. Órgão Responsável
Identifique prefeitura, fundação, consórcio, hospital ou entidade responsável.

# 3. Objeto do Credenciamento
Explique o serviço médico ou assistencial contratado.

# 4. Quem Pode Participar
Explique se aceita PJ, pessoa física, clínica, empresa médica, cooperativa ou profissionais.

# 5. Especialidades e Serviços Aceitos
Liste todas as especialidades, cargos, plantões ou serviços encontrados.

# 6. Valores e Forma de Pagamento
Informe valores, plantões, consultas, hora médica, tabela, forma e prazo de pagamento.

# 7. Prazos Importantes
Liste inscrição, entrega de documentos, vigência, validade do contrato, recursos e datas relevantes.

# 8. Checklist de Documentos
Separe em:
- Documentos da empresa
- Documentos dos médicos/profissionais
- Documentos do responsável técnico
- Certidões negativas
- Outros anexos ou declarações

# 9. Exigências que Podem Impedir a Participação
Aponte exigências como CNES, CRM, RT, alvará, certidões, conta bancária, assinatura digital, experiência, cadastro em sistema ou regularidade fiscal.

# 10. Pontos de Atenção e Riscos
Explique os principais riscos jurídicos, financeiros, documentais e operacionais.

# 11. Informações Não Localizadas
Liste o que não apareceu claramente no edital.

# 12. Próximos Passos Recomendados
Diga exatamente o que a empresa deve fazer agora.

Regras:
- Use linguagem simples.
- Não invente informações.
- Quando algo não estiver localizado, escreva: "Informação não localizada no documento."
- Seja completo, mas direto.

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

            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("## 📋 Resultado da Análise")
            st.markdown(resultado)
            st.markdown("</div>", unsafe_allow_html=True)

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
CredMed IA • MVP experimental para análise de credenciamentos médicos públicos
</div>
""", unsafe_allow_html=True)
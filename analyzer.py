from openai import OpenAI
from pypdf import PdfReader
import streamlit as st

from database import salvar_analise


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(
    api_key=OPENAI_API_KEY
)


def extrair_texto_pdf(uploaded_file):

    pdf_reader = PdfReader(uploaded_file)

    texto = ""

    for page in pdf_reader.pages:

        try:

            texto_extraido = page.extract_text()

            if texto_extraido:
                texto += texto_extraido + "\n"

        except Exception:
            pass

    return texto


def gerar_prompt(texto_pdf):

    prompt = f"""
Você é especialista em:

- Licitações
- Credenciamentos
- Lei 14.133
- Saúde pública
- Contratações médicas
- Editais hospitalares

Faça uma análise COMPLETA deste edital.

A resposta deve conter:

# 1. Resumo Executivo

# 2. Órgão Responsável

# 3. Tipo
Informe se é:
- Credenciamento
- Licitação
- Chamamento Público

# 4. Objeto

# 5. Quem pode participar

# 6. Documentos exigidos

# 7. Valores e pagamentos

# 8. Prazos importantes

# 9. Riscos

# 10. Impedimentos

# 11. Próximos passos

# 12. Conclusão estratégica

Use linguagem clara, prática e profissional.

EDITAL:
{texto_pdf[:15000]}
"""

    return prompt


def analisar_edital(
    uploaded_file,
    user_email
):

    texto_pdf = extrair_texto_pdf(
        uploaded_file
    )

    prompt = gerar_prompt(
        texto_pdf
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    resultado = response.output_text

    salvar_analise(
        uploaded_file.name,
        resultado,
        user_email
    )

    return resultado
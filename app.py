import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# Carrega .env
load_dotenv()

# Pega chave
api_key = os.getenv("OPENAI_API_KEY")

# Conecta OpenAI
client = OpenAI(api_key=api_key)

# Caminho do PDF
caminho_pdf = "editais/edital.pdf"

# Lê PDF
reader = PdfReader(caminho_pdf)

texto = ""

for pagina in reader.pages:
    texto += pagina.extract_text()

print("PDF LIDO COM SUCESSO")
print("-" * 50)

# Prompt da IA
prompt = f"""
Você é uma IA especialista em:

- credenciamento médico
- licitações públicas
- Lei 14.133/2021
- contratação de serviços de saúde
- análise documental
- contratos administrativos

Sua função é analisar editais médicos públicos de forma profissional.

Analise o edital abaixo e gere uma resposta EXTREMAMENTE ORGANIZADA.

A resposta deve conter:

# RESUMO EXECUTIVO
Explique em linguagem simples o objetivo do edital.

# ÓRGÃO RESPONSÁVEL
Informe prefeitura, hospital, UPA, consórcio ou entidade.

# OBJETO DO CREDENCIAMENTO
Explique exatamente o que está sendo contratado.

# QUEM PODE PARTICIPAR
Explique:
- PJ
- pessoa física
- clínicas
- especialidades
- exigências

# ESPECIALIDADES ACEITAS
Liste todas encontradas.

# VALORES E REMUNERAÇÃO
Informe:
- plantões
- consultas
- hora médica
- pagamento
- tabela

# PRAZOS IMPORTANTES
Informe:
- inscrição
- envio de documentos
- validade
- vigência contratual

# CHECKLIST COMPLETO DE DOCUMENTOS

## DOCUMENTOS DA EMPRESA
Liste todos.

## DOCUMENTOS DOS MÉDICOS
Liste todos.

## DOCUMENTOS DO RESPONSÁVEL TÉCNICO
Liste todos.

## CERTIDÕES NEGATIVAS
Liste todas.

# EXIGÊNCIAS IMPORTANTES
Explique:
- CNES
- CRM
- RT
- experiência
- alvarás
- registros

# PONTOS DE RISCO
Explique problemas que podem impedir participação.

# DÚVIDAS OU PONTOS NÃO CLAROS
Mostre informações confusas ou ausentes.

# RECOMENDAÇÃO FINAL
Explique se vale a pena participar e quais os próximos passos.

IMPORTANTE:
- Use linguagem simples.
- Não invente informações.
- Se algo não estiver no edital, escreva:
"Informação não localizada no documento."

EDITAL:
{texto}
"""

# Envia para IA
resposta = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

# Resultado
print(resposta.output_text)
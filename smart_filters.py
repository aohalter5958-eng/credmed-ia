import re


PALAVRAS_SAUDE = [
    "médico",
    "medica",
    "medicina",
    "enfermagem",
    "enfermeiro",
    "farmaceutico",
    "farmácia",
    "hospital",
    "ubs",
    "upa",
    "laboratório",
    "fisioterapia",
    "psicologia",
    "odontologia",
    "saúde",
    "clinica",
    "biomedicina"
]


def texto_oportunidade(item):
    return (
        f"{item.get('titulo', '')} "
        f"{item.get('objetoCompra', '')} "
        f"{item.get('orgaoEntidade', {}).get('razaoSocial', '')}"
    ).lower()


def detectar_tipo(item):
    modalidade = str(item.get("modalidadeNome", "")).lower()

    if "credenciamento" in modalidade:
        return "Credenciamento"

    return "Licitação"


def calcular_score(item):
    texto = texto_oportunidade(item)

    score = 0

    # Saúde
    for palavra in PALAVRAS_SAUDE:
        if palavra in texto:
            score += 10

    # Credenciamento
    modalidade = str(item.get("modalidadeNome", "")).lower()

    if "credenciamento" in modalidade:
        score += 25

    # Hospital / UBS / UPA
    if any(x in texto for x in ["hospital", "ubs", "upa"]):
        score += 20

    # Contratação urgente
    if any(x in texto for x in [
        "urgente",
        "emergencial",
        "imediata"
    ]):
        score += 15

    # Suspenso / cancelado
    if any(x in texto for x in [
        "suspenso",
        "cancelado",
        "fracassado"
    ]):
        score -= 30

    # Limites
    score = max(score, 0)
    score = min(score, 100)

    return score


def classificar_relevancia(score):
    if score >= 90:
        return "🔥 Excelente"

    if score >= 70:
        return "✅ Muito boa"

    if score >= 50:
        return "⚠️ Média"

    return "❌ Fraca"


def oportunidade_relevante(item):
    score = calcular_score(item)
    return score >= 50


def transformar_oportunidade(item):
    score = calcular_score(item)

    orgao = (
        item.get("orgaoEntidade", {})
        .get("razaoSocial", "Não informado")
    )

    municipio = item.get("unidadeOrgao", {}).get("municipioNome", "")
    uf = item.get("unidadeOrgao", {}).get("ufSigla", "")

    local = f"{municipio}/{uf}" if municipio else uf

    return {
        "titulo": item.get("objetoCompra", "Sem título"),
        "orgao": orgao,
        "local": local,
        "modalidade": item.get("modalidadeNome", ""),
        "situacao": item.get("situacaoCompraNome", ""),
        "valor_estimado": item.get("valorTotalEstimado", 0),
        "fim_propostas": item.get("dataEncerramentoProposta", ""),
        "link": item.get("linkSistemaOrigem", ""),
        "score": score,
        "relevancia": classificar_relevancia(score),
        "tipo": detectar_tipo(item)
    }
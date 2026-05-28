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
    partes = [
        str(item.get("titulo", "")),
        str(item.get("objetoCompra", "")),
        str(item.get("informacaoComplementar", "")),
        str(item.get("modalidadeNome", "")),
        str(item.get("situacaoCompraNome", ""))
    ]

    orgao = item.get("orgaoEntidade", {})
    unidade = item.get("unidadeOrgao", {})

    if isinstance(orgao, dict):
        partes.append(str(orgao.get("razaoSocial", "")))

    if isinstance(unidade, dict):
        partes.append(str(unidade.get("municipioNome", "")))
        partes.append(str(unidade.get("ufSigla", "")))

    texto = " ".join(partes)

    texto = texto.lower()

    texto = re.sub(r"\s+", " ", texto)

    return texto


def detectar_tipo(item):
    modalidade = str(
        item.get("modalidadeNome", "")
    ).lower()

    texto = texto_oportunidade(item)

    if (
        "credenciamento" in modalidade
        or "credenciamento" in texto
        or "credenciar" in texto
    ):
        return "Credenciamento"

    return "Licitação"


def calcular_score(item):
    texto = texto_oportunidade(item)

    score = 0

    # Palavras da saúde
    for palavra in PALAVRAS_SAUDE:
        if palavra.lower() in texto:
            score += 10

    # Credenciamento
    if (
        "credenciamento" in texto
        or "credenciar" in texto
    ):
        score += 25

    # Hospital / UBS / UPA
    if any(
        x in texto
        for x in ["hospital", "ubs", "upa"]
    ):
        score += 20

    # Urgência
    if any(
        x in texto
        for x in [
            "urgente",
            "emergencial",
            "imediata"
        ]
    ):
        score += 15

    # Suspenso / cancelado
    if any(
        x in texto
        for x in [
            "suspenso",
            "cancelado",
            "fracassado"
        ]
    ):
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

    unidade = item.get("unidadeOrgao", {})

    municipio = unidade.get(
        "municipioNome",
        ""
    )

    uf = unidade.get(
        "ufSigla",
        ""
    )

    local = (
        f"{municipio}/{uf}"
        if municipio
        else uf
    )

    return {
        "titulo": item.get(
            "objetoCompra",
            "Sem título"
        ),

        "orgao": orgao,

        "local": local,

        "modalidade": item.get(
            "modalidadeNome",
            ""
        ),

        "situacao": item.get(
            "situacaoCompraNome",
            ""
        ),

        "valor_estimado": item.get(
            "valorTotalEstimado",
            0
        ),

        "fim_propostas": item.get(
            "dataEncerramentoProposta",
            ""
        ),

        "link": item.get(
            "linkSistemaOrigem",
            ""
        ),

        "score": score,

        "relevancia": classificar_relevancia(
            score
        ),

        "tipo": detectar_tipo(item)
    }
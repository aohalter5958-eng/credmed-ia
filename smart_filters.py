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
        str(item.get("objetoCompra", "")),
        str(item.get("titulo", "")),
        str(item.get("informacaoComplementar", "")),
        str(item.get("modalidadeNome", "")),
    ]

    orgao = item.get("orgaoEntidade", {})

    if isinstance(orgao, dict):
        partes.append(
            str(orgao.get("razaoSocial", ""))
        )

    return " ".join(partes).lower()


def detectar_tipo(item):

    modalidade = str(
        item.get("modalidadeNome", "")
    ).lower()

    if "credenciamento" in modalidade:
        return "Credenciamento"

    return "Licitação"


def calcular_score(item):

    texto = texto_oportunidade(item)

    score = 0

    for palavra in PALAVRAS_SAUDE:

        if palavra.lower() in texto:
            score += 10

    if "credenciamento" in texto:
        score += 30

    if any(
        x in texto
        for x in [
            "hospital",
            "ubs",
            "upa"
        ]
    ):
        score += 20

    if any(
        x in texto
        for x in [
            "urgente",
            "emergencial",
            "imediata"
        ]
    ):
        score += 15

    if any(
        x in texto
        for x in [
            "cancelado",
            "fracassado",
            "suspenso"
        ]
    ):
        score -= 40

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

    cidade = unidade.get("municipioNome", "")
    uf = unidade.get("ufSigla", "")

    local = f"{cidade}/{uf}"

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


def calcular_match(
    oportunidade_texto,
    profissional
):

    texto = oportunidade_texto.lower()

    pontos = 0

    especialidade = str(
        profissional.get(
            "especialidade",
            ""
        )
    ).lower()

    palavras = str(
        profissional.get(
            "palavras_chave",
            ""
        )
    ).lower()

    experiencia = str(
        profissional.get(
            "experiencia",
            ""
        )
    ).lower()

    profissao = str(
        profissional.get(
            "profissao",
            ""
        )
    ).lower()

    dados_profissional = (
        especialidade
        + " "
        + palavras
        + " "
        + experiencia
        + " "
        + profissao
    )

    for palavra in texto.split():

        if palavra in dados_profissional:
            pontos += 5

    if "plantão" in texto and (
        "plantão" in dados_profissional
    ):
        pontos += 20

    if "upa" in texto and (
        "upa" in dados_profissional
    ):
        pontos += 20

    if "hospital" in texto and (
        "hospital" in dados_profissional
    ):
        pontos += 20

    pontos = min(pontos, 100)

    return pontos
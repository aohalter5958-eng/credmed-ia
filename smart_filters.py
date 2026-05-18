# =========================================
# FILTROS INTELIGENTES CREDMED IA
# =========================================

PALAVRAS_SAUDE = [

    "médico",
    "medica",
    "medicina",
    "enfermeiro",
    "enfermagem",
    "hospital",
    "upa",
    "ubs",
    "plantão",
    "clinico",
    "clínico",
    "psicólogo",
    "psicologia",
    "fisioterapia",
    "fisioterapeuta",
    "odontologia",
    "odontólogo",
    "farmácia",
    "farmaceutico",
    "laboratório",
    "laboratorio",
    "saúde",
    "saude",
    "cirurgia",
    "cirurgião",
    "técnico de enfermagem",
    "terapeuta",
    "fonoaudiólogo",
    "nutricionista",
    "cardiologista",
    "neurologista",
    "ortopedista",
    "pediatra",
    "ginecologista",
    "radiologia",
    "anestesia",
    "ambulância",
    "ambulancia",
    "pronto socorro",
    "samu",
    "credenciamento médico",
    "serviços hospitalares",
    "serviços médicos"

]

# =========================================
# PALAVRAS QUE DEVEM SER EXCLUÍDAS
# =========================================

PALAVRAS_EXCLUIR = [

    "veterinária",
    "veterinario",
    "veterinário",
    "castração animal",
    "ração",
    "cães",
    "gatos",
    "animais",
    "pet",
    "petshop",
    "combustível",
    "combustivel",
    "merenda",
    "uniforme escolar",
    "material de construção",
    "pavimentação",
    "asfalto",
    "limpeza urbana",
    "coleta de lixo",
    "transporte escolar"

]

# =========================================
# CLASSIFICAR RELEVÂNCIA
# =========================================

def calcular_score(texto):

    texto = texto.lower()

    score = 0

    # SOMA PONTOS
    for palavra in PALAVRAS_SAUDE:

        if palavra in texto:
            score += 10

    # REMOVE PONTOS
    for palavra in PALAVRAS_EXCLUIR:

        if palavra in texto:
            score -= 30

    return score


# =========================================
# CLASSIFICAÇÃO
# =========================================

def classificar_relevancia(score):

    if score >= 50:
        return "🟢 Excelente"

    elif score >= 20:
        return "🟡 Média"

    else:
        return "🔴 Baixa"


# =========================================
# VALIDAR SE É SAÚDE REAL
# =========================================

def oportunidade_valida(texto):

    texto = texto.lower()

    # EXCLUIR PALAVRAS RUINS
    for palavra in PALAVRAS_EXCLUIR:

        if palavra in texto:
            return False

    # PRECISA TER PALAVRA DE SAÚDE
    for palavra in PALAVRAS_SAUDE:

        if palavra in texto:
            return True

    return False
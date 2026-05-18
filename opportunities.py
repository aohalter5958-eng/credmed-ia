import requests
import streamlit as st
from datetime import date, timedelta


PNCP_BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"


PALAVRAS_SAUDE = [
    "saúde",
    "saude",
    "médico",
    "medico",
    "médica",
    "medica",
    "hospital",
    "upa",
    "ubs",
    "enfermagem",
    "enfermeiro",
    "enfermeira",
    "fisioterapia",
    "fisioterapeuta",
    "psicologia",
    "psicólogo",
    "psicologo",
    "farmácia",
    "farmacia",
    "farmacêutico",
    "farmaceutico",
    "odontologia",
    "dentista",
    "clínico",
    "clinico",
    "plantão",
    "plantao",
    "ambulância",
    "ambulancia",
    "laboratório",
    "laboratorio",
    "radiologia",
    "exames",
    "serviços médicos",
    "servicos medicos",
]


ESPECIALIDADES = {
    "Todas as áreas da saúde": [],
    "Clínico Geral": ["clínico", "clinico", "médico generalista", "medico generalista"],
    "Enfermagem": ["enfermagem", "enfermeiro", "enfermeira", "técnico de enfermagem", "tecnico de enfermagem"],
    "Fisioterapia": ["fisioterapia", "fisioterapeuta"],
    "Psicologia": ["psicologia", "psicólogo", "psicologo"],
    "Farmácia": ["farmácia", "farmacia", "farmacêutico", "farmaceutico"],
    "Radiologia": ["radiologia", "radiologista", "raio x", "raios x"],
    "Odontologia": ["odontologia", "dentista", "odontólogo", "odontologo"],
}


def formatar_data_api(data_obj):
    return data_obj.strftime("%Y%m%d")


def texto_seguro(valor):
    if valor is None:
        return ""
    return str(valor)


def pegar_campo(item, chaves, padrao="Não informado"):
    for chave in chaves:
        if chave in item and item[chave]:
            return item[chave]
    return padrao


def pegar_orgao(item):
    orgao = item.get("orgaoEntidade")

    if isinstance(orgao, dict):
        return (
            orgao.get("razaoSocial")
            or orgao.get("nomeOrgao")
            or orgao.get("nome")
            or "Órgão não informado"
        )

    return (
        item.get("orgaoEntidadeRazaoSocial")
        or item.get("nomeOrgao")
        or item.get("orgao")
        or "Órgão não informado"
    )


def pegar_cidade_uf(item):
    unidade = item.get("unidadeOrgao")

    cidade = "Cidade não informada"
    uf = ""

    if isinstance(unidade, dict):
        cidade = (
            unidade.get("municipioNome")
            or unidade.get("nomeMunicipio")
            or cidade
        )

        uf = (
            unidade.get("ufSigla")
            or unidade.get("ufNome")
            or ""
        )

    cidade = (
        item.get("municipioNome")
        or item.get("cidade")
        or cidade
    )

    uf = (
        item.get("uf")
        or item.get("ufSigla")
        or uf
    )

    return cidade, uf


def pegar_datas(item):
    abertura = pegar_campo(
        item,
        [
            "dataPublicacaoPncp",
            "dataPublicacao",
            "dataInclusao",
        ],
        "Não informado"
    )

    encerramento = pegar_campo(
        item,
        [
            "dataEncerramentoProposta",
            "dataEncerramento",
            "dataFimRecebimentoProposta",
        ],
        "Não informado"
    )

    return abertura, encerramento


def pegar_link_pncp(item):
    cnpj = (
        item.get("cnpjOrgao")
        or item.get("orgaoEntidade", {}).get("cnpj")
        if isinstance(item.get("orgaoEntidade"), dict)
        else None
    )

    ano = item.get("anoCompra")
    sequencial = item.get("sequencialCompra")

    if cnpj and ano and sequencial:
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"

    numero_controle = item.get("numeroControlePNCP")

    if numero_controle:
        return f"https://pncp.gov.br/app/editais?q={numero_controle}"

    return "https://pncp.gov.br/app/editais"


def montar_texto_busca(item):
    partes = []

    for chave in [
        "objetoCompra",
        "informacaoComplementar",
        "modalidadeNome",
        "modoDisputaNome",
        "situacaoCompraNome",
        "numeroCompra",
        "processo",
    ]:
        partes.append(texto_seguro(item.get(chave)))

    orgao = pegar_orgao(item)
    cidade, uf = pegar_cidade_uf(item)

    partes.append(orgao)
    partes.append(cidade)
    partes.append(uf)

    return " ".join(partes).lower()


def eh_area_saude(texto):
    return any(palavra in texto for palavra in PALAVRAS_SAUDE)


def eh_credenciamento(texto):
    return "credenciamento" in texto or "credenciar" in texto or "credenciado" in texto


def passa_filtros(item, tipo, cidade, especialidade, palavra_chave):
    texto = montar_texto_busca(item)

    if not eh_area_saude(texto):
        return False

    if tipo == "Credenciamento" and not eh_credenciamento(texto):
        return False

    if tipo == "Licitação" and eh_credenciamento(texto):
        return False

    if cidade:
        if cidade.strip().lower() not in texto:
            return False

    termos_especialidade = ESPECIALIDADES.get(especialidade, [])

    if termos_especialidade:
        if not any(termo in texto for termo in termos_especialidade):
            return False

    if palavra_chave:
        if palavra_chave.strip().lower() not in texto:
            return False

    return True


@st.cache_data(ttl=600)
def consultar_pncp(data_final, uf, paginas_maximas):
    resultados = []

    headers = {
        "Accept": "application/json",
        "User-Agent": "CredMed-IA/1.0"
    }

    for pagina in range(1, paginas_maximas + 1):
        params = {
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": 50,
        }

        if uf and uf != "Todos":
            params["uf"] = uf

        try:
            resposta = requests.get(
                PNCP_BASE_URL,
                params=params,
                headers=headers,
                timeout=25
            )

            if resposta.status_code != 200:
                continue

            dados = resposta.json()

            if isinstance(dados, dict):
                itens = (
                    dados.get("data")
                    or dados.get("content")
                    or dados.get("resultado")
                    or []
                )

            elif isinstance(dados, list):
                itens = dados

            else:
                itens = []

            if not itens:
                break

            resultados.extend(itens)

        except Exception:
            continue

    return resultados


def renderizar_card_oportunidade(item):
    titulo = pegar_campo(
        item,
        [
            "objetoCompra",
            "informacaoComplementar",
            "numeroCompra"
        ],
        "Objeto não informado"
    )

    orgao = pegar_orgao(item)
    cidade, uf = pegar_cidade_uf(item)
    abertura, encerramento = pegar_datas(item)

    modalidade = pegar_campo(
        item,
        ["modalidadeNome"],
        "Modalidade não informada"
    )

    situacao = pegar_campo(
        item,
        ["situacaoCompraNome"],
        "Situação não informada"
    )

    valor = pegar_campo(
        item,
        [
            "valorTotalEstimado",
            "valorTotalHomologado",
            "valorGlobal"
        ],
        "Valor não informado"
    )

    link = pegar_link_pncp(item)

    tipo_detectado = "Credenciamento" if eh_credenciamento(montar_texto_busca(item)) else "Licitação"

    st.markdown(f"""
    <div class="card">
        <h3>📄 {titulo[:180]}</h3>

        <p><b>Tipo detectado:</b> {tipo_detectado}</p>
        <p><b>Órgão:</b> {orgao}</p>
        <p><b>Local:</b> {cidade}/{uf}</p>
        <p><b>Modalidade:</b> {modalidade}</p>
        <p><b>Situação:</b> {situacao}</p>
        <p><b>Data de publicação:</b> {abertura}</p>
        <p><b>Fim do recebimento de propostas:</b> {encerramento}</p>
        <p><b>Valor estimado:</b> {valor}</p>

        <p>
            <a href="{link}" target="_blank">
                🔗 Abrir no PNCP
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def tela_oportunidades():
    st.markdown("""
    <div class="card">
        <h2>📡 Radar Real de Oportunidades</h2>
        <p>
        Busca real no PNCP por contratações públicas da área da saúde
        com recebimento de propostas em aberto.
        </p>
        <p>
        Nesta primeira versão real, o radar consulta o PNCP.
        Depois vamos expandir para prefeituras, consórcios, diários oficiais
        e portais municipais específicos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox(
            "Tipo de oportunidade",
            [
                "Credenciamento",
                "Licitação",
                "Todos"
            ]
        )

        uf = st.selectbox(
            "Estado",
            [
                "PR",
                "SP",
                "SC",
                "RS",
                "MG",
                "MS",
                "GO",
                "RJ",
                "ES",
                "BA",
                "PE",
                "CE",
                "Todos"
            ]
        )

        especialidade = st.selectbox(
            "Área / Especialidade",
            list(ESPECIALIDADES.keys())
        )

    with col2:
        cidade = st.text_input(
            "Cidade específica (opcional)"
        )

        palavra_chave = st.text_input(
            "Palavra-chave extra (opcional)",
            placeholder="Ex: UPA, plantão, hospital, laboratório..."
        )

        dias_a_frente = st.slider(
            "Buscar oportunidades abertas até quantos dias à frente?",
            min_value=7,
            max_value=180,
            value=60,
            step=7
        )

    paginas_maximas = st.slider(
        "Profundidade da busca no PNCP",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
        help="Quanto maior, mais registros serão verificados. Pode demorar mais."
    )

    if st.button("🔎 Buscar oportunidades reais"):
        data_final = formatar_data_api(
            date.today() + timedelta(days=dias_a_frente)
        )

        with st.spinner("Consultando PNCP em tempo real..."):
            itens = consultar_pncp(
                data_final=data_final,
                uf=uf,
                paginas_maximas=paginas_maximas
            )

        oportunidades = []

        for item in itens:
            if passa_filtros(
                item=item,
                tipo=tipo,
                cidade=cidade,
                especialidade=especialidade,
                palavra_chave=palavra_chave
            ):
                oportunidades.append(item)

        st.markdown(f"""
        <div class="card">
            <h3>Resultado da busca</h3>
            <p><b>Fonte:</b> PNCP</p>
            <p><b>Registros brutos consultados:</b> {len(itens)}</p>
            <p><b>Oportunidades filtradas:</b> {len(oportunidades)}</p>
        </div>
        """, unsafe_allow_html=True)

        if not oportunidades:
            st.warning(
                "Nenhuma oportunidade encontrada com esses filtros. "
                "Tente ampliar o estado, remover cidade, escolher 'Todos' ou aumentar a profundidade da busca."
            )

        else:
            for item in oportunidades:
                renderizar_card_oportunidade(item)
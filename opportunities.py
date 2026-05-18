import requests
import streamlit as st
from datetime import date, timedelta

from smart_filters import (
    calcular_score,
    classificar_relevancia,
    oportunidade_valida
)


PNCP_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"


def formatar_data_api(data):
    return data.strftime("%Y%m%d")


def consultar_pncp(estado="PR", dias=60, paginas=3):
    resultados = []
    data_final = formatar_data_api(date.today() + timedelta(days=dias))

    headers = {
        "Accept": "application/json",
        "User-Agent": "CredMed-IA/1.0"
    }

    for pagina in range(1, paginas + 1):
        params = {
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": 25
        }

        if estado != "Todos":
            params["uf"] = estado

        try:
            resposta = requests.get(
                PNCP_URL,
                params=params,
                headers=headers,
                timeout=12
            )

            if resposta.status_code != 200:
                continue

            dados = resposta.json()

            itens = dados.get("data", [])

            if not itens:
                break

            resultados.extend(itens)

        except requests.exceptions.Timeout:
            st.warning(
                f"O PNCP demorou demais na página {pagina}. "
                "A busca continuou com os dados já encontrados."
            )
            break

        except Exception as erro:
            st.warning(f"Falha ao consultar página {pagina}: {erro}")
            continue

    return resultados


def texto_item(item):
    partes = []

    for campo in [
        "objetoCompra",
        "informacaoComplementar",
        "modalidadeNome",
        "situacaoCompraNome",
        "numeroCompra",
        "processo"
    ]:
        partes.append(str(item.get(campo, "")))

    orgao = item.get("orgaoEntidade", {})
    unidade = item.get("unidadeOrgao", {})

    if isinstance(orgao, dict):
        partes.append(str(orgao.get("razaoSocial", "")))

    if isinstance(unidade, dict):
        partes.append(str(unidade.get("municipioNome", "")))
        partes.append(str(unidade.get("ufSigla", "")))

    return " ".join(partes).lower()


def eh_credenciamento(texto):
    return (
        "credenciamento" in texto
        or "credenciar" in texto
        or "credenciado" in texto
    )


def passa_filtros(item, tipo, palavra_chave):
    texto = texto_item(item)

    if not oportunidade_valida(texto):
        return False

    if tipo == "Credenciamento" and not eh_credenciamento(texto):
        return False

    if tipo == "Licitação" and eh_credenciamento(texto):
        return False

    if palavra_chave:
        if palavra_chave.lower().strip() not in texto:
            return False

    return True


def pegar_orgao(item):
    orgao = item.get("orgaoEntidade", {})

    if isinstance(orgao, dict):
        return orgao.get("razaoSocial", "Órgão não informado")

    return "Órgão não informado"


def pegar_cidade(item):
    unidade = item.get("unidadeOrgao", {})

    if isinstance(unidade, dict):
        cidade = unidade.get("municipioNome", "Cidade não informada")
        uf = unidade.get("ufSigla", "")
        return f"{cidade}/{uf}"

    return "Local não informado"


def pegar_link(item):
    cnpj = item.get("cnpjOrgao")
    ano = item.get("anoCompra")
    sequencial = item.get("sequencialCompra")

    if cnpj and ano and sequencial:
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"

    return "https://pncp.gov.br/app/editais"


def renderizar_card_oportunidade(item):
    titulo = item.get("objetoCompra", "Objeto não informado")
    orgao = pegar_orgao(item)
    local = pegar_cidade(item)
    link = pegar_link(item)

    modalidade = item.get("modalidadeNome", "Modalidade não informada")
    situacao = item.get("situacaoCompraNome", "Situação não informada")
    valor = item.get("valorTotalEstimado", "Valor não informado")
    encerramento = item.get("dataEncerramentoProposta", "Não informado")

    texto = texto_item(item)
    score = calcular_score(texto)
    relevancia = classificar_relevancia(score)

    tipo = "Credenciamento" if eh_credenciamento(texto) else "Licitação"

    st.markdown(f"""
    <div class="card">
        <h2>📄 {titulo[:220]}</h2>

        <p><b>Tipo detectado:</b> {tipo}</p>
        <p><b>Relevância:</b> {relevancia}</p>
        <p><b>Score inteligente:</b> {score}</p>
        <p><b>Órgão:</b> {orgao}</p>
        <p><b>Local:</b> {local}</p>
        <p><b>Modalidade:</b> {modalidade}</p>
        <p><b>Situação:</b> {situacao}</p>
        <p><b>Fim das propostas:</b> {encerramento}</p>
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
        Busca real no PNCP por licitações e credenciamentos da área da saúde.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox(
            "Tipo de oportunidade",
            ["Todos", "Credenciamento", "Licitação"]
        )

        estado = st.selectbox(
            "Estado",
            ["PR", "SP", "SC", "RS", "MG", "RJ", "Todos"]
        )

    with col2:
        palavra_chave = st.text_input(
            "Palavra-chave opcional",
            placeholder="Ex: médico, hospital, UPA, enfermagem..."
        )

        dias = st.slider(
            "Buscar oportunidades abertas até quantos dias à frente?",
            7,
            120,
            60,
            step=7
        )

    paginas = st.slider(
        "Profundidade da busca",
        1,
        8,
        3,
        help="Use 2 ou 3 para busca rápida. Use mais apenas se necessário."
    )

    if st.button("🔎 Buscar oportunidades reais"):
        with st.spinner("Consultando PNCP em tempo real..."):
            itens = consultar_pncp(
                estado=estado,
                dias=dias,
                paginas=paginas
            )

        oportunidades = []

        for item in itens:
            if passa_filtros(item, tipo, palavra_chave):
                oportunidades.append(item)

        oportunidades = sorted(
            oportunidades,
            key=lambda x: calcular_score(texto_item(x)),
            reverse=True
        )

        st.markdown(f"""
        <div class="card">
            <h2>Resultado da busca</h2>
            <p><b>Fonte:</b> PNCP</p>
            <p><b>Registros brutos consultados:</b> {len(itens)}</p>
            <p><b>Oportunidades filtradas:</b> {len(oportunidades)}</p>
        </div>
        """, unsafe_allow_html=True)

        if not oportunidades:
            st.warning(
                "Nenhuma oportunidade relevante encontrada. "
                "Tente remover palavra-chave, aumentar dias ou escolher Todos."
            )
        else:
            for item in oportunidades:
                renderizar_card_oportunidade(item)
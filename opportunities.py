import requests
import streamlit as st
from datetime import date, timedelta

from smart_filters import calcular_score, classificar_relevancia, oportunidade_valida

PNCP_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"


def consultar_pncp(estado="PR", dias=60, paginas=3):
    resultados = []
    data_final = (date.today() + timedelta(days=dias)).strftime("%Y%m%d")

    for pagina in range(1, paginas + 1):
        params = {
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": 25,
        }

        if estado != "Todos":
            params["uf"] = estado

        try:
            resposta = requests.get(
                PNCP_URL,
                params=params,
                headers={"Accept": "application/json", "User-Agent": "CredMed-IA"},
                timeout=12,
            )

            if resposta.status_code != 200:
                continue

            dados = resposta.json()
            itens = dados.get("data", [])

            if not itens:
                break

            resultados.extend(itens)

        except requests.exceptions.Timeout:
            st.warning(f"O PNCP demorou demais na página {pagina}. A busca continuou.")
            break

        except Exception as erro:
            st.warning(f"Erro ao consultar página {pagina}: {erro}")

    return resultados


def texto_item(item):
    partes = []

    for campo in [
        "objetoCompra",
        "informacaoComplementar",
        "modalidadeNome",
        "situacaoCompraNome",
        "numeroCompra",
        "processo",
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

    if palavra_chave and palavra_chave.lower().strip() not in texto:
        return False

    return True


def pegar_orgao(item):
    orgao = item.get("orgaoEntidade", {})
    if isinstance(orgao, dict):
        return orgao.get("razaoSocial", "Órgão não informado")
    return "Órgão não informado"


def pegar_local(item):
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
    texto = texto_item(item)

    score = calcular_score(texto)
    relevancia = classificar_relevancia(score)
    tipo = "Credenciamento" if eh_credenciamento(texto) else "Licitação"

    with st.container(border=True):
        st.subheader(f"📄 {titulo[:250]}")

        st.write(f"**Tipo detectado:** {tipo}")
        st.write(f"**Relevância:** {relevancia}")
        st.write(f"**Score inteligente:** {score}")
        st.write(f"**Órgão:** {pegar_orgao(item)}")
        st.write(f"**Local:** {pegar_local(item)}")
        st.write(f"**Modalidade:** {item.get('modalidadeNome', 'Não informado')}")
        st.write(f"**Situação:** {item.get('situacaoCompraNome', 'Não informado')}")
        st.write(f"**Fim das propostas:** {item.get('dataEncerramentoProposta', 'Não informado')}")
        st.write(f"**Valor estimado:** R$ {item.get('valorTotalEstimado', 'Não informado')}")

        st.link_button("🔗 Abrir no PNCP", pegar_link(item))


def tela_oportunidades():
    st.markdown("## 📡 Radar Real de Oportunidades")
    st.write("Busca inteligente em tempo real no PNCP.")

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox(
            "Tipo de oportunidade",
            ["Todos", "Credenciamento", "Licitação"],
        )

        estado = st.selectbox(
            "Estado",
            ["PR", "SP", "SC", "RS", "MG", "RJ", "Todos"],
        )

    with col2:
        palavra_chave = st.text_input(
            "Palavra-chave opcional",
            placeholder="Ex: médico, hospital, UPA...",
        )

        dias = st.slider(
            "Buscar oportunidades até quantos dias?",
            7,
            120,
            60,
            step=7,
        )

    paginas = st.slider("Profundidade da busca", 1, 8, 3)

    if st.button("🔎 Buscar oportunidades reais"):
        with st.spinner("Consultando PNCP em tempo real..."):
            itens = consultar_pncp(
                estado=estado,
                dias=dias,
                paginas=paginas,
            )

        oportunidades = [
            item for item in itens
            if passa_filtros(item, tipo, palavra_chave)
        ]

        oportunidades = sorted(
            oportunidades,
            key=lambda x: calcular_score(texto_item(x)),
            reverse=True,
        )

        st.markdown("## Resultado da busca")
        st.write(f"**Fonte:** PNCP")
        st.write(f"**Registros brutos:** {len(itens)}")
        st.write(f"**Oportunidades filtradas:** {len(oportunidades)}")

        if not oportunidades:
            st.warning("Nenhuma oportunidade relevante encontrada.")
        else:
            for item in oportunidades:
                renderizar_card_oportunidade(item)
import requests
import streamlit as st
from datetime import datetime

from smart_filters import (
    calcular_score,
    classificar_relevancia,
    oportunidade_valida
)

# =========================================================
# CONSULTAR PNCP REAL
# =========================================================

def consultar_pncp(
    estado="PR",
    palavra_chave="saude",
    pagina=1,
    tamanho_pagina=50
):

    url = (
        f"https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?"
        f"pagina={pagina}"
        f"&tamanhoPagina={tamanho_pagina}"
        f"&uf={estado}"
        f"&texto={palavra_chave}"
    )

    try:

        response = requests.get(url, timeout=30)

        if response.status_code == 200:

            data = response.json()

            if "data" in data:
                return data["data"]

            return []

        return []

    except Exception as e:

        st.error(f"Erro ao consultar PNCP: {e}")
        return []


# =========================================================
# FORMATAR DATA
# =========================================================

def formatar_data(data_str):

    try:

        data = datetime.fromisoformat(
            data_str.replace("Z", "")
        )

        return data.strftime("%d/%m/%Y")

    except:
        return "Não informado"


# =========================================================
# RENDERIZAR CARD
# =========================================================

def renderizar_card_oportunidade(item):

    titulo = item.get("objetoCompra", "Sem título")

    orgao = item.get(
        "orgaoEntidade",
        {}
    ).get(
        "razaoSocial",
        "Órgão não informado"
    )

    municipio = item.get(
        "unidadeOrgao",
        {}
    ).get(
        "municipioNome",
        "Não informado"
    )

    valor = item.get(
        "valorTotalEstimado",
        0
    )

    data = formatar_data(
        item.get("dataAberturaProposta", "")
    )

    link = item.get("linkSistemaOrigem", "")

    texto_completo = f"""
    {titulo}
    {orgao}
    {municipio}
    """

    score = calcular_score(texto_completo)

    relevancia = classificar_relevancia(score)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(145deg,#16162c,#0d1025);
            padding: 30px;
            border-radius: 22px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.08);
        ">

        <h2 style="color:white;">
        📄 {titulo}
        </h2>

        <p style="color:white;">
        <b>Órgão:</b> {orgao}
        </p>

        <p style="color:white;">
        <b>Cidade:</b> {municipio}
        </p>

        <p style="color:white;">
        <b>Valor estimado:</b>
        R$ {valor:,.2f}
        </p>

        <p style="color:white;">
        <b>Abertura:</b> {data}
        </p>

        <p style="color:white;">
        <b>Relevância:</b> {relevancia}
        </p>

        <p style="color:white;">
        <b>Score Inteligente:</b> {score}
        </p>

        <a href="{link}" target="_blank">
            🔗 Abrir oportunidade
        </a>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# TELA PRINCIPAL
# =========================================================

def tela_oportunidades():

    st.title("🎯 Radar Inteligente de Oportunidades")

    st.write(
        """
        Busque credenciamentos e licitações
        reais da área da saúde diretamente
        do PNCP.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        estado = st.selectbox(
            "Estado",
            [
                "PR",
                "SP",
                "SC",
                "RS",
                "MG",
                "RJ"
            ]
        )

    with col2:

        palavra_chave = st.text_input(
            "Palavra-chave",
            value="médico"
        )

    profundidade = st.slider(
        "Profundidade da busca",
        1,
        20,
        5
    )

    if st.button(
        "🔎 Buscar oportunidades reais"
    ):

        with st.spinner(
            "Consultando PNCP em tempo real..."
        ):

            oportunidades = []

            for pagina in range(1, profundidade + 1):

                dados = consultar_pncp(
                    estado=estado,
                    palavra_chave=palavra_chave,
                    pagina=pagina
                )

                oportunidades.extend(dados)

            oportunidades_filtradas = []

            for item in oportunidades:

                titulo = item.get(
                    "objetoCompra",
                    ""
                )

                if oportunidade_valida(titulo):

                    oportunidades_filtradas.append(item)

            st.success(
                f"""
                Consulta concluída.

                Registros encontrados:
                {len(oportunidades)}

                Oportunidades válidas:
                {len(oportunidades_filtradas)}
                """
            )

            if not oportunidades_filtradas:

                st.warning(
                    "Nenhuma oportunidade relevante encontrada."
                )

            else:

                oportunidades_filtradas = sorted(
                    oportunidades_filtradas,
                    key=lambda x: calcular_score(
                        x.get("objetoCompra", "")
                    ),
                    reverse=True
                )

                for item in oportunidades_filtradas:

                    renderizar_card_oportunidade(item)
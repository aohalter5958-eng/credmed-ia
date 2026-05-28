import requests
import streamlit as st
from datetime import date, timedelta

from smart_filters import (
    calcular_score,
    classificar_relevancia,
    oportunidade_relevante,
    transformar_oportunidade,
    calcular_match
)

from database import (
    salvar_oportunidade,
    buscar_oportunidades
)

from professionals import buscar_profissionais


PNCP_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"


def consultar_pncp(
    estado,
    dias,
    paginas
):

    resultados = []

    data_final = (
        date.today() + timedelta(days=dias)
    ).strftime("%Y%m%d")

    headers = {
        "Accept": "application/json",
        "User-Agent": "CredMed-IA"
    }

    for pagina in range(1, paginas + 1):

        params = {
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": 50
        }

        if estado != "Todos":
            params["uf"] = estado

        try:

            response = requests.get(
                PNCP_URL,
                params=params,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                continue

            dados = response.json()

            itens = dados.get("data", [])

            if not itens:
                break

            resultados.extend(itens)

        except Exception as erro:
            st.warning(
                f"Erro ao consultar PNCP: {erro}"
            )

    return resultados


def renderizar_match(
    oportunidade,
    profissionais
):

    texto = (
        oportunidade.get("titulo", "")
        + " "
        + oportunidade.get("orgao", "")
    )

    matches = []

    for profissional in profissionais:

        pontos = calcular_match(
            texto,
            profissional
        )

        if pontos >= 30:

            matches.append({
                "nome": profissional.get("nome"),
                "profissao": profissional.get("profissao"),
                "especialidade": profissional.get("especialidade"),
                "score": pontos,
                "cidade": profissional.get("cidade"),
                "estado": profissional.get("estado")
            })

    matches = sorted(
        matches,
        key=lambda x: x["score"],
        reverse=True
    )

    if matches:

        st.markdown("### 👥 Profissionais compatíveis")

        for match in matches[:5]:

            st.markdown(
                f"""
                <div style="
                    background:#111827;
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:10px;
                    border:1px solid rgba(255,255,255,0.06);
                ">

                <b>{match['nome']}</b><br>

                {match['profissao']} —
                {match['especialidade']}<br>

                📍 {match['cidade']}/{match['estado']}<br>

                🎯 Compatibilidade:
                <b>{match['score']}%</b>

                </div>
                """,
                unsafe_allow_html=True
            )


def renderizar_card(item):

    st.markdown(
        f"""
        <div style="
            background:#0f1230;
            padding:25px;
            border-radius:20px;
            margin-bottom:20px;
            border:1px solid rgba(255,255,255,0.08);
        ">

        <h2 style="color:white;">
            📄 {item['titulo']}
        </h2>

        <p><b>Tipo:</b> {item['tipo']}</p>

        <p><b>Relevância:</b>
        {item['relevancia']}</p>

        <p><b>Score:</b>
        {item['score']}</p>

        <p><b>Órgão:</b>
        {item['orgao']}</p>

        <p><b>Local:</b>
        {item['local']}</p>

        <p><b>Modalidade:</b>
        {item['modalidade']}</p>

        <p><b>Situação:</b>
        {item['situacao']}</p>

        <p><b>Valor estimado:</b>
        R$ {item['valor_estimado']}</p>

        <a href="{item['link']}"
           target="_blank"
           style="
           display:inline-block;
           margin-top:10px;
           padding:10px 18px;
           background:#8b5cf6;
           color:white;
           text-decoration:none;
           border-radius:10px;
           font-weight:bold;
           ">
           🔗 Abrir no PNCP
        </a>

        </div>
        """,
        unsafe_allow_html=True
    )

    profissionais = buscar_profissionais()

    renderizar_match(
        item,
        profissionais
    )


def tela_oportunidades():

    st.title("Radar de Oportunidades")

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
                "RJ",
                "Todos"
            ]
        )

    with col2:

        dias = st.slider(
            "Buscar oportunidades até quantos dias?",
            7,
            180,
            60,
            step=7
        )

    paginas = st.slider(
        "Quantidade de páginas PNCP",
        1,
        10,
        3
    )

    if st.button(
        "🔎 Buscar oportunidades reais"
    ):

        with st.spinner(
            "Consultando PNCP..."
        ):

            itens = consultar_pncp(
                estado,
                dias,
                paginas
            )

        oportunidades = []

        for item in itens:

            if oportunidade_relevante(item):

                oportunidade = (
                    transformar_oportunidade(item)
                )

                oportunidades.append(
                    oportunidade
                )

        oportunidades = sorted(
            oportunidades,
            key=lambda x: x["score"],
            reverse=True
        )

        salvas = 0

        for item in oportunidades:

            if salvar_oportunidade(item):
                salvas += 1

        st.success(
            f"✅ {salvas} oportunidades salvas automaticamente."
        )

        st.write(
            f"Resultados encontrados: {len(oportunidades)}"
        )

        if not oportunidades:

            st.warning(
                "Nenhuma oportunidade relevante encontrada."
            )

        else:

            for item in oportunidades:

                renderizar_card(item)